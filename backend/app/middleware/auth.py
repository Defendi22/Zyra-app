"""
Middleware de Autenticação — Valida JWT tokens do Supabase
Injeta user_id no request.state para uso em endpoints
Verifica token blacklist no Redis para logout.
"""

import logging
from typing import Callable, Optional

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import jwt
from jwt import DecodeError, ExpiredSignatureError

from app.config import settings
from app.cache.redis_client import redis_client

logger = logging.getLogger("zyra.auth")


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Valida JWT token no header Authorization: Bearer <token>
    Sempre inicializa request.state.user_id (None se sem token)
    Endpoints protegidos usam Depends(require_auth)
    """

    BEARER_PREFIX = "Bearer "
    PUBLIC_PATHS = {
        "/health",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/api/v1/auth/login",
        "/api/v1/auth/register",
    }

    async def dispatch(self, request: Request, call_next: Callable) -> any:
        # Sempre inicializar state — evita AttributeError nos outros middlewares
        request.state.user_id = None
        request.state.user = None

        # Paths públicos — pular validação de token
        if request.url.path in self.PUBLIC_PATHS:
            return await call_next(request)

        # Extrair token do header
        auth_header = request.headers.get("Authorization", "")
        logger.debug(f"Auth header presente: {bool(auth_header)} | path: {request.url.path}")

        if not auth_header.startswith(self.BEARER_PREFIX):
            # Sem token — continuar (require_auth vai rejeitar se necessário)
            return await call_next(request)

        token = auth_header[len(self.BEARER_PREFIX):]

        try:
            # Verificar blacklist no Redis (logout)
            blacklist_key = f"token_blacklist:{token}"
            try:
                is_blacklisted = await redis_client.exists(blacklist_key)
                if is_blacklisted:
                    logger.warning("Token na blacklist (logout)")
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "Token invalidado"},
                        headers={"WWW-Authenticate": "Bearer"},
                    )
            except Exception as e:
                logger.warning(f"Redis check failed (non-critical): {e}")

            # Decodificar JWT
            decoded = jwt.decode(
                token,
                settings.SUPABASE_ANON_KEY,
                algorithms=["HS256"],
            )

            user_id = decoded.get("sub")
            if not user_id:
                raise ValueError("Token sem claim 'sub'")

            # Injetar no request.state
            request.state.user_id = user_id
            request.state.user = decoded
            logger.debug(f"Auth OK — user_id: {user_id}")

        except ExpiredSignatureError:
            logger.warning("Token expirado")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token expirado"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        except DecodeError as e:
            logger.warning(f"Token inválido: {e}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token inválido"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        except Exception as e:
            logger.error(f"Erro ao validar token: {e}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Erro na autenticação"},
            )

        return await call_next(request)


def require_auth(request: Request) -> str:
    """Dependency para garantir que user_id existe"""
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticação requerida",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id