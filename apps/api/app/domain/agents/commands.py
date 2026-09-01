from dataclasses import dataclass

@dataclass(frozen=True)
class CreateAgent:
    actor_id: str
    tenant_id: str
    correlation_id: str
    reason: str | None = None

@dataclass(frozen=True)
class ReviewAgent:
    identifier: str
    actor_id: str
    decision: str
    reason: str
