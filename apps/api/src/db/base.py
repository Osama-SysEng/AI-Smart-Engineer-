"""SQLAlchemy Base with common columns."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class TimestampMixin:
    """Mixin for timestamp columns."""
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class AuditMixin:
    """Mixin for audit columns."""
    created_by: Mapped[str] = mapped_column(String(255), nullable=True)
    updated_by: Mapped[str] = mapped_column(String(255), nullable=True)
    version: Mapped[int] = mapped_column(default=1)


class SoftDeleteMixin:
    """Mixin for soft delete."""
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(default=False)


class UUIDMixin:
    """Mixin for UUID primary key."""
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
