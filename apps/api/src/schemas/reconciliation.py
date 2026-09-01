"""Reconciliation schemas."""
from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel


class ReconciliationRunCreate(BaseModel):
    project_id: str
    site_id: str | None = None
    name: str
    sources_compared: List[str]


class ReconciliationItemResponse(BaseModel):
    id: str
    reconciliation_run_id: str
    item_code: str
    description: str | None
    source_values: Dict[str, float | str]
    variance: float | None
    variance_percentage: float | None
    status: str
    root_cause: str | None
    confidence: float | None
    recommended_action: str | None
    approved: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ReconciliationRunResponse(BaseModel):
    id: str
    project_id: str
    site_id: str | None
    name: str
    status: str
    sources_compared: List[str]
    started_at: datetime | None
    completed_at: datetime | None
    total_items: int
    matched_count: int
    variance_count: int
    error_count: int
    summary: str | None
    items: List[ReconciliationItemResponse] = []

    class Config:
        from_attributes = True
