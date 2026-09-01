"""Workflow, Task, and Approval models."""
from typing import List

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, UUIDMixin


class Workflow(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "workflows"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    trigger_type: Mapped[str] = mapped_column(String(100), nullable=False)
    trigger_config: Mapped[dict] = mapped_column(JSON, nullable=False)
    steps: Mapped[list] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id"), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_by: Mapped[str] = mapped_column(String(36), nullable=False)

    runs: Mapped[List["WorkflowRun"]] = relationship("WorkflowRun", back_populates="workflow")


class WorkflowRun(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "workflow_runs"

    workflow_id: Mapped[str] = mapped_column(ForeignKey("workflows.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    trigger_event: Mapped[str] = mapped_column(String(255), nullable=False)
    context: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    current_step: Mapped[int] = mapped_column(Integer, default=0)
    total_steps: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    trace_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    workflow: Mapped["Workflow"] = relationship("Workflow", back_populates="runs")


class Task(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "tasks"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False)
    site_id: Mapped[str | None] = mapped_column(ForeignKey("sites.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    assigned_to: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_by: Mapped[str] = mapped_column(String(36), nullable=False)
    due_date: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    metadata_payload: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)


class Approval(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "approvals"

    request_type: Mapped[str] = mapped_column(String(100), nullable=False)
    request_id: Mapped[str] = mapped_column(String(36), nullable=False)
    requested_by: Mapped[str] = mapped_column(String(36), nullable=False)
    approver_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    impact_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    approved_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_payload: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
