"""Procurement and inventory models."""
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base, TimestampMixin, UUIDMixin


class Supplier(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "suppliers"

    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(100), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    metadata_payload: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)


class PurchaseOrder(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "purchase_orders"

    po_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    supplier_id: Mapped[str | None] = mapped_column(ForeignKey("suppliers.id"), nullable=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False)
    site_id: Mapped[str | None] = mapped_column(ForeignKey("sites.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="draft")
    total_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    order_date: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivery_date: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sap_reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    metadata_payload: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)


class InventoryTransaction(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "inventory_transactions"

    material_id: Mapped[str] = mapped_column(ForeignKey("materials.id"), nullable=False)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False)
    site_id: Mapped[str | None] = mapped_column(ForeignKey("sites.id"), nullable=True)
    transaction_type: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    reference_doc: Mapped[str | None] = mapped_column(String(255), nullable=True)
    transaction_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    sap_reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    metadata_payload: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
