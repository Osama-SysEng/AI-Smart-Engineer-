"""Audit router."""
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from src.db.session import get_db
from src.db.models.audit import AuditLog, SystemEvent
from src.db.models.user import User
from src.security.auth import get_current_user, require_permissions
from src.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/logs")
async def get_audit_logs(
    resource_type: str | None = None,
    action: str | None = None,
    user_id: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("audit:read"))
):
    """Get audit logs."""
    query = select(AuditLog).join(User, AuditLog.user_id == User.id, isouter=True)
    if not current_user.is_superuser:
        query = query.where((AuditLog.user_id.is_(None)) | (User.tenant_id == current_user.tenant_id))
    if resource_type:
        query = query.where(AuditLog.resource_type == resource_type)
    if action:
        query = query.where(AuditLog.action == action)
    if user_id:
        query = query.where(AuditLog.user_id == user_id)

    query = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/events")
async def get_system_events(
    severity: str | None = None,
    resolved: bool | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("audit:read"))
):
    """Get system events."""
    query = select(SystemEvent)
    if severity:
        query = query.where(SystemEvent.severity == severity)
    if resolved is not None:
        query = query.where(SystemEvent.resolved == resolved)

    query = query.order_by(SystemEvent.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()
