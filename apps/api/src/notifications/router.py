"""Notifications router."""
from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from src.db.session import get_db
from src.db.models.notification import Notification
from src.db.models.user import User
from src.security.auth import get_current_user
from src.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("")
async def get_notifications(
    unread_only: bool = False,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user notifications."""
    query = select(Notification).where(Notification.user_id == current_user.id)
    if unread_only:
        query = query.where(Notification.read == False)
    query = query.order_by(Notification.created_at.desc()).limit(limit)
    result = await db.execute(query)
    notifications = result.scalars().all()

    unread_count = sum(1 for n in notifications if not n.read)
    return {"notifications": notifications, "unread_count": unread_count}


@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark notification as read."""
    result = await db.execute(
        select(Notification).where(
            and_(Notification.id == notification_id, Notification.user_id == current_user.id)
        )
    )
    notification = result.scalar_one_or_none()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.read = True
    notification.read_at = datetime.now()
    await db.commit()
    return {"success": True}


@router.post("/mark-all-read")
async def mark_all_notifications_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark all notifications as read."""
    result = await db.execute(
        select(Notification).where(
            and_(Notification.user_id == current_user.id, Notification.read == False)
        )
    )
    notifications = result.scalars().all()
    for notification in notifications:
        notification.read = True
        notification.read_at = datetime.now()
    await db.commit()
    return {"success": True, "count": len(notifications)}
