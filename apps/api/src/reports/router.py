"""Reports router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.db.models.project import Project, Site

from src.db.session import get_db
from src.db.models.user import User
from src.security.auth import get_current_user, require_permissions
from src.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/generate")
async def generate_report(
    report_type: str,
    project_id: str | None = None,
    site_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("report:generate"))
):
    """Generate a report."""
    if project_id:
        result = await db.execute(select(Project).where(Project.id == project_id, Project.tenant_id == current_user.tenant_id, Project.is_deleted == False))
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Project not found")
    if site_id:
        result = await db.execute(select(Site).join(Project, Project.id == Site.project_id).where(Site.id == site_id, Project.tenant_id == current_user.tenant_id, Site.is_deleted == False))
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Site not found")
    from src.queue.tasks import generate_report_task

    job_id = generate_report_task.delay(
        report_type=report_type,
        project_id=project_id,
        site_id=site_id,
        date_from=date_from,
        date_to=date_to,
        user_id=current_user.id,
    )
    return {"job_id": job_id.id, "status": "queued", "message": "Report generation started"}


@router.get("/types")
async def list_report_types(
    current_user: User = Depends(get_current_user)
):
    """List available report types."""
    return {
        "types": [
            {"id": "daily", "name": "Daily Report"},
            {"id": "weekly", "name": "Weekly Report"},
            {"id": "monthly", "name": "Monthly Report"},
            {"id": "project", "name": "Project Report"},
            {"id": "site", "name": "Site Report"},
            {"id": "material", "name": "Material Report"},
            {"id": "cost", "name": "Cost Report"},
            {"id": "quality", "name": "Quality Report"},
            {"id": "reconciliation", "name": "Reconciliation Report"},
            {"id": "anomaly", "name": "Anomaly Report"},
        ]
    }
