"""Analytics router."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta

from src.db.session import get_db
from src.db.models.user import User
from src.db.models.document import Document
from src.db.models.extraction import ExtractionRun
from src.db.models.reconciliation import ReconciliationRun
from src.db.models.workflow import Task
from src.db.models.project import Project
from src.security.auth import get_current_user, require_permissions
from src.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_analytics(
    project_id: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard analytics."""
    # Document stats
    doc_query = select(func.count(Document.id)).join(Project, Project.id == Document.project_id).where(Document.is_deleted == False, Project.tenant_id == current_user.tenant_id)
    if project_id:
        doc_query = doc_query.where(Document.project_id == project_id)
    doc_result = await db.execute(doc_query)
    total_documents = doc_result.scalar() or 0

    # Processing stats
    processing_query = select(func.count(Document.id)).join(Project, Project.id == Document.project_id).where(
        and_(Document.is_deleted == False, Document.status == "processing", Project.tenant_id == current_user.tenant_id)
    )
    if project_id:
        processing_query = processing_query.where(Document.project_id == project_id)
    processing_result = await db.execute(processing_query)
    processing_docs = processing_result.scalar() or 0

    # Error count
    error_query = select(func.sum(Document.error_count)).join(Project, Project.id == Document.project_id).where(Document.is_deleted == False, Project.tenant_id == current_user.tenant_id)
    if project_id:
        error_query = error_query.where(Document.project_id == project_id)
    error_result = await db.execute(error_query)
    total_errors = error_result.scalar() or 0

    # Pending tasks
    task_query = select(func.count(Task.id)).join(Project, Project.id == Task.project_id).where(Task.status == "pending", Project.tenant_id == current_user.tenant_id)
    if project_id:
        task_query = task_query.where(Task.project_id == project_id)
    task_result = await db.execute(task_query)
    pending_tasks = task_result.scalar() or 0

    # Reconciliation variance
    recon_query = select(func.count(ReconciliationRun.id)).join(Project, Project.id == ReconciliationRun.project_id).where(
        ReconciliationRun.variance_count > 0, Project.tenant_id == current_user.tenant_id
    )
    if project_id:
        recon_query = recon_query.where(ReconciliationRun.project_id == project_id)
    recon_result = await db.execute(recon_query)
    variance_count = recon_result.scalar() or 0

    return {
        "total_documents": total_documents,
        "processing_documents": processing_docs,
        "total_errors": total_errors,
        "pending_tasks": pending_tasks,
        "variance_count": variance_count,
        "automation_rate": 0.0,
        "data_quality_score": 0.0,
        "sap_sync_success_rate": 0.0,
    }


@router.get("/kpis")
async def get_kpis(
    period: str = "monthly",
    project_id: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("analytics:read"))
):
    """Return KPI values derived from tenant-scoped data; never return fabricated metrics."""
    doc_query = select(func.count(Document.id)).join(Project, Project.id == Document.project_id).where(Document.is_deleted == False, Project.tenant_id == current_user.tenant_id)
    if project_id:
        doc_query = doc_query.where(Document.project_id == project_id)
    result = await db.execute(doc_query)
    documents_processed = result.scalar() or 0

    task_query = select(func.count(Task.id)).join(Project, Project.id == Task.project_id).where(Project.tenant_id == current_user.tenant_id, Task.status == "pending")
    if project_id:
        task_query = task_query.where(Task.project_id == project_id)
    result = await db.execute(task_query)
    pending_tasks = result.scalar() or 0

    return {
        "period": period,
        "kpis": {
            "documents_processed": documents_processed,
            "pending_tasks": pending_tasks,
            "automation_rate": None,
            "manual_hours_saved": None,
            "avg_processing_time_minutes": None,
            "error_rate": None,
            "reconciliation_accuracy": None,
            "anomaly_count": None,
            "critical_issues": None,
            "pending_approvals": None,
            "sap_sync_success_rate": None,
        },
        "note": "Metrics not persisted yet are returned as null; system never fabricates operational KPIs.",
    }
