from dataclasses import dataclass

@dataclass(frozen=True)
class CreateErp:
    actor_id: str
    tenant_id: str
    correlation_id: str
    reason: str | None = None

@dataclass(frozen=True)
class ReviewErp:
    identifier: str
    actor_id: str
    decision: str
    reason: str
