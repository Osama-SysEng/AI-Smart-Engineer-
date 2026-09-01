"""AI chat schemas."""
from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel


class AIChatRequest(BaseModel):
    message: str
    context: Dict | None = None
    project_id: str | None = None
    site_id: str | None = None
    thread_id: str | None = None
    model_override: str | None = None


class AIChatResponse(BaseModel):
    response: str
    intent: str | None
    tools_used: List[str] = []
    data_sources: List[str] = []
    confidence: float | None
    requires_approval: bool = False
    suggested_actions: List[Dict] = []
    trace_id: str
    latency_ms: int
    cost_estimate: float | None


class AIUsageResponse(BaseModel):
    period: str
    provider: str
    model: str
    total_requests: int
    total_tokens_in: int
    total_tokens_out: int
    total_cost: float
    avg_latency_ms: float | None

    class Config:
        from_attributes = True
