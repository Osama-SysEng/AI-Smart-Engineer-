"""Cost tracking model."""
from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base, TimestampMixin, UUIDMixin


class CostRecord(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "cost_records"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False)
    site_id: Mapped[str | None] = mapped_column(ForeignKey("sites.id"), nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    item_code: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    planned_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    variance: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    period: Mapped[str] = mapped_column(String(50), nullable=False)
    cost_type: Mapped[str] = mapped_column(String(50), nullable=False)
    sap_reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    metadata_payload: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
