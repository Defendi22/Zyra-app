"""
Configurações da aplicação — carrega de .env
"""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # ==================== APP ====================
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_VERSION: str = "1.0.0"

    # ==================== SERVER ====================
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ==================== CORS ====================
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8081",
        "exp://localhost:8081",
    ]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "*.railway.app"]

    # ==================== AUTH ====================
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    JWT_SECRET: str = "your-secret-key-change-in-prod"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # ==================== DATABASE ====================
    SUPABASE_CONNECTION_TIMEOUT: int = 10

    # ==================== CACHE ====================
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600
    REDIS_RATE_LIMIT_WINDOW: int = 60

    # ==================== RATE LIMIT ====================
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    RATE_LIMIT_REQUESTS_PER_HOUR: int = 1000
    RATE_LIMIT_BYPASS_PATHS: List[str] = [
        "/health",
        "/docs",
        "/openapi.json",
        "/api/v1/auth/login",
        "/api/v1/auth/register",
    ]

    # ==================== xAI GROK ====================
    XAI_API_KEY: str = ""
    XAI_MODEL: str = "grok-3-mini"
    XAI_VISION_MODEL: str = "grok-4.20"

    # ==================== STORAGE ====================
    R2_ACCOUNT_ID: str = ""
    R2_ACCESS_KEY_ID: str = ""
    R2_SECRET_ACCESS_KEY: str = ""
    R2_BUCKET_URL: str = "https://zyra.cdn.example.com"
    R2_MAX_FILE_SIZE_MB: int = 10

    # ==================== FEATURES ====================
    FEATURE_AI_MEAL_ANALYSIS: bool = True
    FEATURE_APPLE_HEALTHKIT: bool = True
    FEATURE_GOOGLE_FIT: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True

    def get_cors_origins(self) -> List[str]:
        if self.ENVIRONMENT == "production":
            return ["https://zyra.app", "https://www.zyra.app"]
        return self.CORS_ORIGINS


settings = Settings()