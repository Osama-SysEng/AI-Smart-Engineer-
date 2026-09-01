from dataclasses import dataclass

@dataclass(frozen=True)
class CreateApproval:
    actor_id: str
    tenant_id: str
    correlation_id: str
    reason: str | None = None

@dataclass(frozen=True)
class ReviewApproval:
    identifier: str
    actor_id: str
    decision: str
    reason: str
