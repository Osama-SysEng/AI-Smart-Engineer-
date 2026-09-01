from datetime import datetime
from pydantic import BaseModel, Field

class ApprovalSnapshot(BaseModel):
    identifier: str = Field(min_length=1, max_length=150)
    status: str = Field(min_length=1, max_length=40)
    tenant_id: str | None = None
    correlation_id: str | None = None
    updated_at: datetime | None = None

class ApprovalPage(BaseModel):
    items: list[ApprovalSnapshot] = Field(default_factory=list)
    next_cursor: str | None = None
