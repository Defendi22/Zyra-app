"""
Middleware de Logging — Estruturado com request_id
"""

import time
import logging
import uuid
from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("zyra.http")


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Adiciona request_id e loga tempo de resposta
    """

    async def dispatch(self, request: Request, call_next: Callable) -> any:
        # Gerar request_id
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        # Tempo de início
        start_time = time.time()

        # Log de entrada
        logger.info(
            f"{request_id} | {request.method} {request.url.path} | "
            f"Client: {request.client.host}"
        )

        try:
            # Processar request
            response = await call_next(request)

            # Calcular tempo de resposta
            process_time = time.time() - start_time

            # Log de saída
            logger.info(
                f"{request_id} | {request.method} {request.url.path} | "
                f"Status: {response.status_code} | "
                f"Duration: {process_time:.3f}s"
            )

            # Adicionar request_id header
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            # Log de erro
            process_time = time.time() - start_time
            logger.error(
                f"{request_id} | {request.method} {request.url.path} | "
                f"Error: {e} | Duration: {process_time:.3f}s",
                exc_info=True,
            )
            raise
