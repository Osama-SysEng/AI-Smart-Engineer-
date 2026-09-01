"""Database session management."""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.core.config import get_settings

settings = get_settings()

engine_options = {"echo": settings.DEBUG}
if not settings.async_database_url.startswith("sqlite"):
    engine_options.update({
        "pool_size": settings.DATABASE_POOL_SIZE,
        "max_overflow": settings.DATABASE_MAX_OVERFLOW,
        "pool_timeout": settings.DATABASE_POOL_TIMEOUT_SECONDS,
        "pool_recycle": settings.DATABASE_POOL_RECYCLE_SECONDS,
        "pool_pre_ping": True,
        "connect_args": {
            "timeout": settings.DATABASE_CONNECT_TIMEOUT_SECONDS,
            "server_settings": {"application_name": settings.DATABASE_APPLICATION_NAME},
        },
    })
    if settings.DATABASE_SSL_MODE == "require":
        engine_options["connect_args"]["ssl"] = "require"

engine = create_async_engine(settings.async_database_url, **engine_options)

async_session = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
