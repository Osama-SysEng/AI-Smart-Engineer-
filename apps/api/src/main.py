"""AI Smart Engineer - FastAPI Main Application."""
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from src.core.config import get_settings
from src.core.logging import configure_logging, get_logger
from src.core.exceptions import AIEngineerException
from src.db.session import engine
from src.db.base import Base
from src.queue.celery_app import celery_app

# Import routers
from src.auth.router import router as auth_router
from src.projects.router import router as projects_router
from src.documents.router import router as documents_router
from src.extraction.router import router as extraction_router
from src.reconciliation.router import router as reconciliation_router
from src.workflows.router import router as workflows_router
from src.ai.router import router as ai_router
from src.reports.router import router as reports_router
from src.analytics.router import router as analytics_router
from src.notifications.router import router as notifications_router
from src.audit.router import router as audit_router
from src.health.router import router as health_router
from src.security.router import router as security_router

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    settings.validate_runtime_security()
    logger.info("Starting AI Smart Engineer API...")
    # Create tables (use Alembic in production)
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.create_all)
        pass
    yield
    logger.info("Shutting down AI Smart Engineer API...")
    await engine.dispose()


settings = get_settings()
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Engineering Intelligence & Automation Platform",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID and logging."""
    import uuid
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    logger.info(
        "Request started",
        method=request.method,
        path=request.url.path,
        request_id=request_id,
        client=request.client.host if request.client else None,
    )

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    logger.info(
        "Request completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        request_id=request_id,
    )
    return response


@app.exception_handler(AIEngineerException)
async def ai_engineer_exception_handler(request: Request, exc: AIEngineerException):
    return JSONResponse(
        status_code=400,
        content={
            "code": exc.__class__.__name__,
            "message": str(exc),
            "request_id": getattr(request.state, "request_id", None),
            "retryable": False,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception", error=str(exc), exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred",
            "request_id": getattr(request.state, "request_id", None),
            "retryable": True,
        },
    )


# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(projects_router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(documents_router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(extraction_router, prefix="/api/v1/extraction", tags=["Extraction"])
app.include_router(reconciliation_router, prefix="/api/v1/reconciliation", tags=["Reconciliation"])
app.include_router(workflows_router, prefix="/api/v1/workflows", tags=["Workflows"])
app.include_router(ai_router, prefix="/api/v1/ai", tags=["AI"])
app.include_router(reports_router, prefix="/api/v1/reports", tags=["Reports"])
app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(notifications_router, prefix="/api/v1/notifications", tags=["Notifications"])
app.include_router(audit_router, prefix="/api/v1/audit", tags=["Audit"])
app.include_router(security_router, prefix="/api/v1/security", tags=["Security & RBAC"])
app.include_router(health_router, prefix="/api/v1/health", tags=["Health"])


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
    }
