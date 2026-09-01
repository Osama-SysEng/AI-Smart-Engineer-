"""Extraction schemas."""
from datetime import datetime
from typing import List

from pydantic import BaseModel


class ExtractionRunCreate(BaseModel):
    document_id: str
    pipeline_type: str = "auto"
    model_override: str | None = None


class ExtractionRunResponse(BaseModel):
    id: str
    document_id: str
    pipeline_type: str
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    total_entities: int
    success_count: int
    error_count: int
    avg_confidence: float | None
    model_used: str | None
    processing_time_ms: int | None

    class Config:
        from_attributes = True
