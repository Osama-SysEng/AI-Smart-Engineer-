"""Engineering and material models."""
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base, TimestampMixin, UUIDMixin


class EngineeringItem(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "engineering_items"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False)
    site_id: Mapped[str | None] = mapped_column(ForeignKey("sites.id"), nullable=True)
    item_code: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    source_document_id: Mapped[str | None] = mapped_column(ForeignKey("documents.id"), nullable=True)
    source_revision: Mapped[str | None] = mapped_column(String(50), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    normalized: Mapped[bool] = mapped_column(Boolean, default=False)
    metadata_payload: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)


class Material(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "materials"

    code: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    specifications: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    aliases: Mapped[list | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
