"""Document schemas."""
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class DocumentUpload(BaseModel):
    project_id: str
    site_id: str | None = None
    metadata: dict | None = None


class DocumentResponse(BaseModel):
    id: str
    project_id: str
    site_id: str | None
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    mime_type: str
    status: str
    processing_progress: int
    confidence: float | None
    extracted_count: int
    error_count: int
    warning_count: int
    review_required: bool
    virus_scanned: bool
    virus_clean: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExtractedEntityResponse(BaseModel):
    id: str
    document_id: str
    entity_type: str
    entity_subtype: str | None
    value: str
    normalized_value: str | None
    confidence: float
    page_number: int | None
    bounding_box: dict | None
    source_region: str | None
    validation_status: str
    approved: bool
    created_at: datetime

    class Config:
        from_attributes = True
