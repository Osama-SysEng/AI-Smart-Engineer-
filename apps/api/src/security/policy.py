"""Tenant-aware authorization policy evaluation independent of HTTP transport."""
from dataclasses import dataclass

from src.db.models.user import User


@dataclass(frozen=True)
class AuthorizationDecision:
    """A machine-readable policy decision suitable for an audit record."""

    allowed: bool
    permission: str
    reason: str
    tenant_id: str


def evaluate_permission(
    user: User,
    *,
    resource: str,
    action: str,
    resource_tenant_id: str | None = None,
) -> AuthorizationDecision:
    """Evaluate a permission using tenant isolation before role permissions."""
    permission = f"{resource}:{action}"
    effective_tenant = resource_tenant_id or user.tenant_id
    if not user.is_active:
        return AuthorizationDecision(False, permission, "inactive_user", effective_tenant)
    if resource_tenant_id and resource_tenant_id != user.tenant_id and not user.is_superuser:
        return AuthorizationDecision(False, permission, "tenant_boundary", effective_tenant)
    if user.is_superuser:
        return AuthorizationDecision(True, permission, "superuser", effective_tenant)
    for role in user.roles:
        if role.tenant_id not in (None, user.tenant_id):
            continue
        for granted in role.permissions:
            if granted.resource == resource and granted.action == action:
                return AuthorizationDecision(True, permission, f"role:{role.name}", effective_tenant)
    return AuthorizationDecision(False, permission, "permission_missing", effective_tenant)
