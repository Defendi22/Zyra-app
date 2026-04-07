"""
Middleware de Autenticação — Valida JWT tokens do Supabase
Injeta user_id no request.state para uso em endpoints
Verifica token blacklist no Redis para logout
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
    Valida JWT token do Supabase no header Authorization: Bearer <token>
    Endpoints públicos (sem token) continuam funcionando — use @require_auth no endpoint
    Verifica Redis blacklist para logout
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
        # Paths públicos — pular validação
        if request.url.path in self.PUBLIC_PATHS:
            return await call_next(request)

        # Extrair token do header
        auth_header = request.headers.get("Authorization", "")
        logger.debug(f"Authorization header: {auth_header[:50] if auth_header else 'MISSING'}")

        if not auth_header.startswith(self.BEARER_PREFIX):
            # Token ausente — continuar (endpoint pode ser público)
            # Se o endpoint precisar de auth, use @require_auth
            logger.debug(f"No token for {request.url.path}")
            request.state.user_id = None
            request.state.user = None
            return await call_next(request)

        token = auth_header[len(self.BEARER_PREFIX) :]

        try:
            # Verificar se token está na blacklist (logout)
            blacklist_key = f"token_blacklist:{token}"
            try:
                is_blacklisted = await redis_client.exists(blacklist_key)
                if is_blacklisted:
                    logger.warning("❌ Token invalidado (logout)")
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "Token invalidado"},
                        headers={"WWW-Authenticate": "Bearer"},
                    )
            except Exception as e:
                logger.warning(f"Redis check failed (non-critical): {e}")
                # Continuar mesmo se Redis falha

            # Decodificar JWT do Supabase
            decoded = jwt.decode(
                token,
                settings.SUPABASE_ANON_KEY,
                algorithms=["HS256"],
            )

            # Extrair user_id (sub = subject claim)
            user_id = decoded.get("sub")
            if not user_id:
                raise ValueError("Token missing 'sub' claim")

            # Adicionar user_id ao request state
            request.state.user_id = user_id
            request.state.user = decoded

            logger.debug(f"✅ Auth OK — user_id: {user_id}")

        except ExpiredSignatureError:
            logger.warning(f"❌ Token expirado")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token expirado"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        except DecodeError as e:
            logger.warning(f"❌ Token inválido: {e}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token inválido"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        except Exception as e:
            logger.error(f"❌ Erro ao validar token: {e}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Erro na autenticação"},
            )

        return await call_next(request)


def require_auth(request: Request) -> str:
    """Dependency para garantir que user_id existe"""
    if not request.state.user_id:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticação requerida",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return request.state.user_id
