"""Security-focused audit helpers that reuse the core evidence ledger."""
from typing import Any

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.audit import AuditLog


def request_context(request: Request | None) -> dict[str, str | None]:
    """Return a minimal, privacy-conscious request context for audit records."""
    if request is None:
        return {"source_ip": None, "user_agent": None, "request_id": None, "trace_id": None}
    forwarded = request.headers.get("x-forwarded-for", "")
    source_ip = forwarded.split(",")[0].strip() if forwarded else (request.client.host if request.client else None)
    return {
        "source_ip": source_ip,
        "user_agent": request.headers.get("user-agent"),
        "request_id": request.headers.get("x-request-id"),
        "trace_id": request.headers.get("x-trace-id"),
    }


async def record_security_event(
    db: AsyncSession,
    *,
    action: str,
    user_id: str | None,
    outcome: str,
    request: Request | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Append an authentication or authorization decision to the audit ledger."""
    context = request_context(request)
    db.add(
        AuditLog(
            user_id=user_id,
            action=action,
            resource_type="security",
            reason=outcome,
            source_ip=context["source_ip"],
            user_agent=context["user_agent"],
            request_id=context["request_id"],
            trace_id=context["trace_id"],
            metadata_payload=metadata or {},
        )
    )
