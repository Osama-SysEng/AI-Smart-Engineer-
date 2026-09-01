from dataclasses import dataclass

@dataclass(frozen=True)
class CreateReconciliation:
    actor_id: str
    tenant_id: str
    correlation_id: str
    reason: str | None = None

@dataclass(frozen=True)
class ReviewReconciliation:
    identifier: str
    actor_id: str
    decision: str
    reason: str
