"""Document and extraction models."""
from typing import List

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, UUIDMixin, SoftDeleteMixin


class Document(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "documents"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False)
    site_id: Mapped[str | None] = mapped_column(ForeignKey("sites.id"), nullable=True)
    uploaded_by: Mapped[str] = mapped_column(String(36), nullable=False)
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="uploaded")
    processing_progress: Mapped[int] = mapped_column(Integer, default=0)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    extracted_count: Mapped[int] = mapped_column(Integer, default=0)
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    warning_count: Mapped[int] = mapped_column(Integer, default=0)
    review_required: Mapped[bool] = mapped_column(Boolean, default=False)
    virus_scanned: Mapped[bool] = mapped_column(Boolean, default=False)
    virus_clean: Mapped[bool] = mapped_column(Boolean, default=True)
    metadata_payload: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="documents")
    site: Mapped["Site"] = relationship("Site", back_populates="documents")
    versions: Mapped[List["DocumentVersion"]] = relationship("DocumentVersion", back_populates="document")
    pages: Mapped[List["DocumentPage"]] = relationship("DocumentPage", back_populates="document")
    entities: Mapped[List["ExtractedEntity"]] = relationship("ExtractedEntity", back_populates="document")


class DocumentVersion(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "document_versions"

    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    changes_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    diff_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_by: Mapped[str] = mapped_column(String(36), nullable=False)

    document: Mapped["Document"] = relationship("Document", back_populates="versions")


class DocumentPage(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "document_pages"

    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), nullable=False)
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    ocr_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    layout_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    image_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    width: Mapped[float | None] = mapped_column(Float, nullable=True)
    height: Mapped[float | None] = mapped_column(Float, nullable=True)

    document: Mapped["Document"] = relationship("Document", back_populates="pages")


class ExtractedEntity(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "extracted_entities"

    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), nullable=False)
    extraction_run_id: Mapped[str] = mapped_column(ForeignKey("extraction_runs.id"), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_subtype: Mapped[str | None] = mapped_column(String(100), nullable=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bounding_box: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    source_region: Mapped[str | None] = mapped_column(String(255), nullable=True)
    validation_status: Mapped[str] = mapped_column(String(50), default="pending")
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    metadata_payload: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)

    document: Mapped["Document"] = relationship("Document", back_populates="entities")
