"""Workflow schemas."""
from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel


class WorkflowCreate(BaseModel):
    name: str
    description: str | None = None
    trigger_type: str
    trigger_config: Dict
    steps: List[Dict]
    project_id: str | None = None


class WorkflowResponse(BaseModel):
    id: str
    name: str
    description: str | None
    trigger_type: str
    is_active: bool
    project_id: str | None
    version: int
    created_by: str
    created_at: datetime

    class Config:
        from_attributes = True


class WorkflowRunResponse(BaseModel):
    id: str
    workflow_id: str
    status: str
    trigger_event: str
    current_step: int
    total_steps: int
    started_at: datetime | None
    completed_at: datetime | None
    trace_id: str | None

    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    project_id: str
    site_id: str | None = None
    title: str
    description: str | None = None
    priority: str = "medium"
    assigned_to: str | None = None
    due_date: datetime | None = None
    source: str | None = None
    source_id: str | None = None


class TaskResponse(BaseModel):
    id: str
    project_id: str
    site_id: str | None
    title: str
    description: str | None
    status: str
    priority: str
    assigned_to: str | None
    created_by: str
    due_date: datetime | None
    completed_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True
