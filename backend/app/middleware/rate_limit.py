"""
Middleware de Rate Limiting — Usa Redis Sliding Window Counter
"""

import logging
from typing import Callable

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.cache.redis_client import redis_client

logger = logging.getLogger("zyra.rate_limit")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Implementa rate limiting usando Redis Sliding Window Counter.
    - 60 requisições por minuto (default)
    - 1000 requisições por hora
    """

    async def dispatch(self, request: Request, call_next: Callable) -> any:
        # Pular rate limit em paths específicos
        if request.url.path in settings.RATE_LIMIT_BYPASS_PATHS:
            return await call_next(request)

        try:
            # Identificar cliente (user_id se autenticado, IP se não)
            client_id = (
                request.state.user_id
                if hasattr(request.state, "user_id") and request.state.user_id
                else request.client.host
            )

            # Chaves Redis
            minute_key = f"rate_limit:1m:{client_id}"
            hour_key = f"rate_limit:1h:{client_id}"

            # Verificar limite de 1 minuto
            minute_count = await redis_client.incr(minute_key)
            if minute_count == 1:
                # Primeira requisição neste minuto — expirar em 60s
                await redis_client.expire(minute_key, 60)

            if minute_count > settings.RATE_LIMIT_REQUESTS_PER_MINUTE:
                logger.warning(f"🚫 Rate limit (1m) exceeded for {client_id}")
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Muitas requisições — tente novamente em 1 minuto",
                        "retry_after": 60,
                    },
                    headers={"Retry-After": "60"},
                )

            # Verificar limite de 1 hora
            hour_count = await redis_client.incr(hour_key)
            if hour_count == 1:
                await redis_client.expire(hour_key, 3600)

            if hour_count > settings.RATE_LIMIT_REQUESTS_PER_HOUR:
                logger.warning(f"🚫 Rate limit (1h) exceeded for {client_id}")
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Limite horário excedido",
                        "retry_after": 3600,
                    },
                    headers={"Retry-After": "3600"},
                )

        except Exception as e:
            # Se Redis falha, continuar (graceful degradation)
            logger.warning(f"⚠️ Rate limit check failed: {e}")

        return await call_next(request)
