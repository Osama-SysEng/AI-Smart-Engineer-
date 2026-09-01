"""Project schemas."""
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class SiteCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    location: str | None = None
    status: str = "active"
    manager_id: str | None = None
    metadata: dict | None = None


class SiteResponse(BaseModel):
    id: str
    project_id: str
    name: str
    code: str
    location: str | None
    status: str
    manager_id: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    description: str | None = None
    head_id: str | None = None


class DepartmentResponse(BaseModel):
    id: str
    project_id: str
    name: str
    code: str
    description: str | None
    head_id: str | None

    class Config:
        from_attributes = True


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    client: str | None = None
    location: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    budget: float | None = None
    currency: str = "USD"
    metadata: dict | None = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str | None
    client: str | None
    location: str | None
    status: str
    start_date: datetime | None
    end_date: datetime | None
    budget: float | None
    currency: str
    health_score: int
    tenant_id: str
    created_at: datetime
    sites: List[SiteResponse] = []
    departments: List[DepartmentResponse] = []

    class Config:
        from_attributes = True
