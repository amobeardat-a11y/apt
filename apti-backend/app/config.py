import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # Application
    PROJECT_NAME: str = "APTI - Nền tảng Ôn luyện Aptitude Test Tiếng Việt"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # Security & JWT
    SECRET_KEY: str = "super-secret-key-change-in-production-apti-2026-neon-secure"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    BCRYPT_ROUNDS: int = 12

    # Database: Neon PostgreSQL (supports connection string with asyncpg)
    # Example Neon URL: postgresql+asyncpg://neondb_owner:npg_xxx@ep-xyz.region.aws.neon.tech/neondb?ssl=require
    # Fallback to local SQLite async for testing/development when no Neon credentials provided
    DATABASE_URL: str = "sqlite+aiosqlite:///./apti.db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 300  # 5 minutes, recommended for Neon serverless pooler
    DB_POOL_PRE_PING: bool = True

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Rate Limiting (Security against Brute-Force & DoS)
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_GENERAL_PER_MINUTE: int = 120
    RATE_LIMIT_AUTH_PER_MINUTE: int = 10
    MAX_FAILED_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_MINUTES: int = 15

    # Payment & Webhook Security
    PAYMENT_WEBHOOK_SECRET: str = "apti-webhook-secret-key-neon-secure"

    # Default Super Admin Seed
    FIRST_SUPERUSER_EMAIL: str = "admin@apti.vn"
    FIRST_SUPERUSER_PASSWORD: str = "Apti@2026Admin!"
    FIRST_SUPERUSER_NAME: str = "APTI System Administrator"


settings = Settings()
