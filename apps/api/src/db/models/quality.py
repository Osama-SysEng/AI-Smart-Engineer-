"""Quality and work order models."""
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base, TimestampMixin, UUIDMixin


class QualityRecord(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "quality_records"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False)
    site_id: Mapped[str | None] = mapped_column(ForeignKey("sites.id"), nullable=True)
    inspection_type: Mapped[str] = mapped_column(String(100), nullable=False)
    item_code: Mapped[str | None] = mapped_column(String(255), nullable=True)
    result: Mapped[str] = mapped_column(String(50), nullable=False)
    inspector: Mapped[str | None] = mapped_column(String(255), nullable=True)
    inspection_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    attachments: Mapped[list | None] = mapped_column(JSON, nullable=True)
    metadata_payload: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)


class WorkOrder(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "work_orders"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False)
    site_id: Mapped[str | None] = mapped_column(ForeignKey("sites.id"), nullable=True)
    wo_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    assigned_to: Mapped[str | None] = mapped_column(String(36), nullable=True)
    start_date: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    due_date: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_date: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    estimated_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    sap_reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    metadata_payload: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
