"""
ZYRA Backend — FastAPI Main Application
Roteamento por domínio, middleware de auth + rate limit, error handling.
"""

import time
import logging
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings
from app.middleware.auth import AuthMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.logging import LoggingMiddleware
from app.routes.v1 import auth, social, health, ai
from app.cache.redis_client import redis_client
from app.db.supabase_client import supabase_client

# ==================== LIFESPAN ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup e shutdown hooks"""
    # Startup
    logger = logging.getLogger("zyra")
    logger.info("🚀 ZYRA Backend iniciando...")

    try:
        # Conectar Redis
        await redis_client.connect()
        logger.info("✅ Redis conectado")
    except Exception as e:
        logger.error(f"❌ Redis unavailable: {e}")
        # Não falhar aqui — Redis é opcional em dev

    try:
        # Conectar Supabase (opcional por enquanto)
        supabase_client.connect()
        logger.info("✅ Supabase conectado")
    except Exception as e:
        logger.warning(f"⚠️ Supabase unavailable (continuing without DB): {e}")
        # Continuar sem Supabase — vamos usar só pra testes

    yield

    # Shutdown
    logger.info("👋 ZYRA Backend encerrando...")
    await redis_client.close()

# ==================== FASTAPI APP ====================

# ==================== FASTAPI APP ====================

app = FastAPI(
    title="ZYRA API",
    description="Rede Social Fitness — Backend API",
    version="1.0.0",
    lifespan=lifespan,
)

# ==================== SECURITY SCHEME ====================

security = HTTPBearer()


def custom_openapi():
    """Custom OpenAPI schema com Bearer token"""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="ZYRA API",
        version="1.0.0",
        description="Rede Social Fitness — Backend API",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT access token. Get from /api/v1/auth/login or /api/v1/auth/register",
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# ==================== MIDDLEWARE ====================

# 1. CORS (deve ser first)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Trusted Host
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)

# 3. Logging (antes de Auth para capturar todas as requests)
app.add_middleware(LoggingMiddleware)

# 4. Rate Limit
app.add_middleware(RateLimitMiddleware)

# 5. Auth (valida JWT)
app.add_middleware(AuthMiddleware)

# ==================== ROUTES ====================

# Health check (public)
@app.get("/health", tags=["System"])
async def health_check():
    """Verificar saúde da API"""
    return {
        "status": "ok",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }

# API v1 routes (com prefixo)
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(social.router, prefix="/api/v1/social", tags=["Social"])
app.include_router(health.router, prefix="/api/v1/health", tags=["Health"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI"])

# ==================== ERROR HANDLERS ====================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global para exceções não capturadas"""
    logger = logging.getLogger("zyra")
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "request_id": request.headers.get("x-request-id", "unknown"),
        },
    )

# ==================== LOGGING ====================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
    )
