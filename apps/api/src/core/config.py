"""Application configuration using Pydantic Settings."""
from functools import lru_cache
from secrets import token_urlsafe
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    APP_NAME: str = "AI Smart Engineer"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    MAX_REQUEST_BODY_MB: int = 10

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost/db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT_SECONDS: int = 30
    DATABASE_POOL_RECYCLE_SECONDS: int = 1800
    DATABASE_CONNECT_TIMEOUT_SECONDS: int = 10
    DATABASE_SSL_MODE: str = "prefer"
    DATABASE_APPLICATION_NAME: str = "ai-smart-engineer-api"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = Field(default_factory=lambda: token_urlsafe(48))
    ALGORITHM: str = "HS256"
    JWT_ISSUER: str = "ai-smart-engineer"
    JWT_AUDIENCE: str = "ai-smart-engineer-api"
    REQUIRE_SESSION_BOUND_TOKENS: bool = True
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    MFA_ENABLED: bool = True

    # AI Providers
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    LOCAL_LLM_URL: str = "http://localhost:11434"

    DEFAULT_AI_PROVIDER: str = "openai"
    DEFAULT_AI_MODEL: str = "gpt-4o"
    FALLBACK_PROVIDER: str = "deepseek"
    LOCAL_MODEL_ENABLED: bool = True

    # AI Cost Control
    AI_COST_LIMIT_DAILY: float = 100.0  # USD
    AI_COST_LIMIT_MONTHLY: float = 2000.0

    # SAP
    SAP_HOST: Optional[str] = None
    SAP_PORT: int = 8000
    SAP_USER: Optional[str] = None
    SAP_PASSWORD: Optional[str] = None
    SAP_CLIENT: str = "100"
    SAP_CLIENT_ID: Optional[str] = None
    SAP_CLIENT_SECRET: Optional[str] = None
    SAP_TOKEN_URL: Optional[str] = None
    SAP_ALLOWED_HOSTS: List[str] = []
    SAP_TIMEOUT_SECONDS: int = 10
    SAP_ASHOST: Optional[str] = None
    SAP_SYSNR: str = "00"
    SAP_READ_ONLY: bool = True
    SAP_DRY_RUN: bool = True
    SAP_MOCK_MODE: bool = False

    # Storage
    STORAGE_TYPE: str = "local"
    STORAGE_PATH: str = "/app/storage"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_S3_BUCKET: Optional[str] = None
    AWS_REGION: str = "us-east-1"

    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # Monitoring
    SENTRY_DSN: Optional[str] = None

    # Features
    ENABLE_AI_CHAT: bool = True
    ENABLE_SAP_SYNC: bool = True
    ENABLE_WORKFLOW_AUTOMATION: bool = True
    ENABLE_ANOMALY_DETECTION: bool = True
    ENABLE_REAL_TIME_UPDATES: bool = True

    # Multi-tenant
    MULTI_TENANT_ENABLED: bool = False
    DEFAULT_TENANT: str = "default"

    # File Upload
    MAX_FILE_SIZE_MB: int = 100
    ALLOWED_EXTENSIONS: List[str] = [
        ".pdf", ".xlsx", ".xls", ".csv", ".docx", ".doc",
        ".jpg", ".jpeg", ".png", ".tiff", ".tif", ".dwg"
    ]

    # Confidence Thresholds
    CONFIDENCE_AUTO_ACCEPT: float = 0.95
    CONFIDENCE_REVIEW: float = 0.80

    def validate_runtime_security(self) -> None:
        if self.DEBUG or self.ENVIRONMENT in {"development", "test"}:
            return
        if "SECRET_KEY" not in self.model_fields_set or len(self.SECRET_KEY) < 32:
            raise RuntimeError("SECRET_KEY must be explicitly supplied and at least 32 characters in production")
        if "*" in self.CORS_ORIGINS:
            raise RuntimeError("Wildcard CORS is forbidden in production")
        if self.DATABASE_URL.startswith("postgresql") and self.DATABASE_SSL_MODE != "require":
            raise RuntimeError("Managed PostgreSQL must require TLS in production")

    # Vector DB
    QDRANT_URL: str = "http://localhost:6333"

    @property
    def async_database_url(self) -> str:
        return self.DATABASE_URL


@lru_cache()
def get_settings() -> Settings:
    return Settings()
