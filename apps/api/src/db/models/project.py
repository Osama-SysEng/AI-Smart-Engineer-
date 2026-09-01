"""Project, Site, and Department models."""
from typing import List

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, UUIDMixin, SoftDeleteMixin


class Project(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    client: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active")
    start_date: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_date: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    budget: Mapped[float | None] = mapped_column(nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    tenant_id: Mapped[str] = mapped_column(String(36), default="default")
    metadata_payload: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    health_score: Mapped[int] = mapped_column(Integer, default=100)

    sites: Mapped[List["Site"]] = relationship("Site", back_populates="project")
    departments: Mapped[List["Department"]] = relationship("Department", back_populates="project")
    documents: Mapped[List["Document"]] = relationship("Document", back_populates="project")


class Site(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "sites"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active")
    manager_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    metadata_payload: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="sites")
    documents: Mapped[List["Document"]] = relationship("Document", back_populates="site")


class Department(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "departments"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    head_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="departments")
