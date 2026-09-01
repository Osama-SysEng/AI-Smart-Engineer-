"""Extraction router."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.db.session import get_db
from src.db.models.extraction import ExtractionRun
from src.db.models.user import User
from src.db.models.document import Document
from src.db.models.project import Project
from src.security.auth import get_current_user, require_permissions
from src.schemas.extraction import ExtractionRunCreate, ExtractionRunResponse
from src.queue.tasks import run_extraction_task
from src.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/run", response_model=ExtractionRunResponse, status_code=status.HTTP_202_ACCEPTED)
async def run_extraction(
    extraction_data: ExtractionRunCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("extraction:run"))
):
    """Start an extraction run."""
    owner = await db.execute(select(Document).join(Project, Project.id == Document.project_id).where(Document.id == extraction_data.document_id, Project.tenant_id == current_user.tenant_id, Document.is_deleted == False))
    if not owner.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Document not found")

    run = ExtractionRun(
        document_id=extraction_data.document_id,
        pipeline_type=extraction_data.pipeline_type,
        status="queued",
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)

    run_extraction_task.delay(str(run.id), extraction_data.model_override)
    logger.info("Extraction queued", run_id=run.id, document_id=extraction_data.document_id)
    return run


@router.get("/runs/{run_id}", response_model=ExtractionRunResponse)
async def get_extraction_run(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get extraction run status."""
    result = await db.execute(select(ExtractionRun).join(Document, Document.id == ExtractionRun.document_id).join(Project, Project.id == Document.project_id).where(ExtractionRun.id == run_id, Project.tenant_id == current_user.tenant_id))
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Extraction run not found")
    return run


@router.get("/runs", response_model=List[ExtractionRunResponse])
async def list_extraction_runs(
    document_id: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List extraction runs."""
    query = select(ExtractionRun).join(Document, Document.id == ExtractionRun.document_id).join(Project, Project.id == Document.project_id).where(Project.tenant_id == current_user.tenant_id).offset(skip).limit(limit).order_by(ExtractionRun.created_at.desc())
    if document_id:
        query = query.where(ExtractionRun.document_id == document_id)
    result = await db.execute(query)
    return result.scalars().all()
