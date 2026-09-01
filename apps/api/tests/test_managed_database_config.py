"""Configuration contracts for managed PostgreSQL deployment safety."""
import pytest

from src.core.config import Settings


def test_production_requires_tls_for_postgresql():
    settings = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="a" * 48,
        CORS_ORIGINS=["https://app.example.com"],
        DATABASE_URL="postgresql+asyncpg://db.example.com/engineer",
        DATABASE_SSL_MODE="prefer",
    )
    with pytest.raises(RuntimeError, match="TLS"):
        settings.validate_runtime_security()


def test_production_accepts_required_tls_for_postgresql():
    settings = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="a" * 48,
        CORS_ORIGINS=["https://app.example.com"],
        DATABASE_URL="postgresql+asyncpg://db.example.com/engineer",
        DATABASE_SSL_MODE="require",
    )
    settings.validate_runtime_security()


def test_production_rejects_generated_fallback_secret():
    settings = Settings(
        ENVIRONMENT="production",
        CORS_ORIGINS=["https://app.example.com"],
        DATABASE_URL="postgresql+asyncpg://db.example.com/engineer",
        DATABASE_SSL_MODE="require",
    )
    with pytest.raises(RuntimeError, match="explicitly supplied"):
        settings.validate_runtime_security()
