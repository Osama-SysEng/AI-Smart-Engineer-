"""Reconciliation router."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.db.session import get_db
from src.db.models.reconciliation import ReconciliationRun, ReconciliationItem
from src.db.models.user import User
from src.security.auth import get_current_user, require_permissions
from src.schemas.reconciliation import ReconciliationRunCreate, ReconciliationRunResponse, ReconciliationItemResponse
from src.queue.tasks import run_reconciliation_task
from src.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/run", response_model=ReconciliationRunResponse, status_code=status.HTTP_202_ACCEPTED)
async def run_reconciliation(
    data: ReconciliationRunCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("reconciliation:run"))
):
    """Start a reconciliation run."""
    run = ReconciliationRun(
        project_id=data.project_id,
        site_id=data.site_id,
        name=data.name,
        sources_compared=data.sources_compared,
        status="queued",
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)

    run_reconciliation_task.delay(str(run.id))
    logger.info("Reconciliation queued", run_id=run.id, project_id=data.project_id)
    return run


@router.get("/runs/{run_id}", response_model=ReconciliationRunResponse)
async def get_reconciliation_run(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get reconciliation run with items."""
    result = await db.execute(
        select(ReconciliationRun).where(ReconciliationRun.id == run_id)
    )
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Reconciliation run not found")
    return run


@router.get("/runs/{run_id}/items", response_model=List[ReconciliationItemResponse])
async def get_reconciliation_items(
    run_id: str,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get reconciliation items."""
    query = select(ReconciliationItem).where(ReconciliationItem.reconciliation_run_id == run_id)
    if status:
        query = query.where(ReconciliationItem.status == status)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/items/{item_id}/approve")
async def approve_reconciliation_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("reconciliation:approve"))
):
    """Approve a reconciliation item."""
    result = await db.execute(select(ReconciliationItem).where(ReconciliationItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.approved = True
    item.approved_by = current_user.id
    await db.commit()
    logger.info("Reconciliation item approved", item_id=item_id, user_id=current_user.id)
    return {"success": True, "message": "Item approved"}
