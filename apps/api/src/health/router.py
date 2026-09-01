"""Health check router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis.asyncio as redis

from src.db.session import get_db
from src.core.config import get_settings
from src.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("")
async def health_check():
    """Basic health check."""
    return {"status": "healthy", "service": "ai-smart-engineer-api"}


@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Readiness check with DB."""
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        logger.error("Readiness check failed", error=str(e))
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"status": "not_ready", "database": "disconnected"}) from e


@router.get("/live")
async def liveness_check():
    """Liveness check."""
    return {"status": "alive"}


@router.get("/dependencies")
async def dependency_check(db: AsyncSession = Depends(get_db)):
    """Check all dependencies."""
    settings = get_settings()
    checks = {
        "api": "healthy",
        "database": "unknown",
        "redis": "unknown",
        "storage": "unknown",
    }

    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "connected"
    except Exception as e:
        checks["database"] = f"error: {str(e)}"

    # Check Redis
    try:
        r = redis.from_url(settings.REDIS_URL)
        await r.ping()
        checks["redis"] = "connected"
        await r.close()
    except Exception as e:
        checks["redis"] = f"error: {str(e)}"

    return checks
