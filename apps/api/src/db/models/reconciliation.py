"""Reconciliation models."""
from typing import List

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, UUIDMixin


class ReconciliationRun(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "reconciliation_runs"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False)
    site_id: Mapped[str | None] = mapped_column(ForeignKey("sites.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    sources_compared: Mapped[list] = mapped_column(JSON, nullable=False)
    started_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    total_items: Mapped[int] = mapped_column(Integer, default=0)
    matched_count: Mapped[int] = mapped_column(Integer, default=0)
    variance_count: Mapped[int] = mapped_column(Integer, default=0)
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_payload: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)

    items: Mapped[List["ReconciliationItem"]] = relationship("ReconciliationItem", back_populates="run")


class ReconciliationItem(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "reconciliation_items"

    reconciliation_run_id: Mapped[str] = mapped_column(ForeignKey("reconciliation_runs.id"), nullable=False)
    item_code: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_values: Mapped[dict] = mapped_column(JSON, nullable=False)
    variance: Mapped[float | None] = mapped_column(Float, nullable=True)
    variance_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    recommended_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    metadata_payload: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)

    run: Mapped["ReconciliationRun"] = relationship("ReconciliationRun", back_populates="items")
