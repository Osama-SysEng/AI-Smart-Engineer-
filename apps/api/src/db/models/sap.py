"""SAP integration records."""
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base, TimestampMixin, UUIDMixin


class SAPRecord(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "sap_records"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False)
    site_id: Mapped[str | None] = mapped_column(ForeignKey("sites.id"), nullable=True)
    sap_table: Mapped[str] = mapped_column(String(100), nullable=False)
    sap_key: Mapped[str] = mapped_column(String(255), nullable=False)
    record_type: Mapped[str] = mapped_column(String(100), nullable=False)
    data: Mapped[dict] = mapped_column(JSON, nullable=False)
    sync_status: Mapped[str] = mapped_column(String(50), default="pending")
    sync_direction: Mapped[str] = mapped_column(String(20), default="import")
    last_sync_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sync_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    is_dry_run: Mapped[bool] = mapped_column(Boolean, default=False)
    metadata_payload: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
