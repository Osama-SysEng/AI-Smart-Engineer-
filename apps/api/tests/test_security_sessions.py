"""Regression tests for session-bound authentication and policy decisions."""
from uuid import uuid4

from httpx import AsyncClient

from src.db.models.user import Permission, Role, User
from src.security.policy import evaluate_permission


async def _register_and_login(client: AsyncClient, prefix: str) -> dict:
    unique = f"{prefix}-{uuid4().hex[:8]}"
    register = await client.post(
        "/api/v1/auth/register",
        json={
            "email": f"{unique}@example.com",
            "username": unique,
            "password": "safe-pass-123",
            "full_name": "Security Test User",
        },
    )
    assert register.status_code == 201
    login = await client.post("/api/v1/auth/login", json={"username": unique, "password": "safe-pass-123"})
    assert login.status_code == 200
    return login.json()


async def test_refresh_rotates_token_and_replay_revokes_session(client: AsyncClient):
    tokens = await _register_and_login(client, "rotation")
    first_refresh = tokens["refresh_token"]

    rotated = await client.post("/api/v1/auth/refresh", json={"refresh_token": first_refresh})
    assert rotated.status_code == 200
    new_refresh = rotated.json()["refresh_token"]
    assert new_refresh != first_refresh

    replay = await client.post("/api/v1/auth/refresh", json={"refresh_token": first_refresh})
    assert replay.status_code == 401
    revoked_session = await client.post("/api/v1/auth/refresh", json={"refresh_token": new_refresh})
    assert revoked_session.status_code == 401


async def test_logout_revokes_access_to_current_session(client: AsyncClient):
    tokens = await _register_and_login(client, "logout")
    client.headers["Authorization"] = f"Bearer {tokens['access_token']}"
    response = await client.post("/api/v1/auth/logout")
    assert response.status_code == 204
    me = await client.get("/api/v1/auth/me")
    assert me.status_code == 401


async def test_security_admin_can_provision_tenant_role(auth_client: AsyncClient):
    suffix = uuid4().hex[:8]
    permission_response = await auth_client.post(
        "/api/v1/security/permissions",
        json={"name": f"reviews-read-{suffix}", "resource": "reviews", "action": "read"},
    )
    assert permission_response.status_code == 201
    role_response = await auth_client.post(
        "/api/v1/security/roles",
        json={"name": f"reviewer-{suffix}", "description": "Can review engineering evidence"},
    )
    assert role_response.status_code == 201
    permission_id = permission_response.json()["id"]
    role_id = role_response.json()["id"]
    grant_permission = await auth_client.post(f"/api/v1/security/roles/{role_id}/permissions/{permission_id}")
    assert grant_permission.status_code == 204

    target_name = f"review-target-{suffix}"
    target = await auth_client.post(
        "/api/v1/auth/register",
        json={
            "email": f"{target_name}@example.com",
            "username": target_name,
            "password": "safe-pass-123",
            "full_name": "Role Target",
        },
    )
    assert target.status_code == 201
    grant_role = await auth_client.post(f"/api/v1/security/users/{target.json()['id']}/roles/{role_id}")
    assert grant_role.status_code == 204

    login = await auth_client.post("/api/v1/auth/login", json={"username": target_name, "password": "safe-pass-123"})
    auth_client.headers["Authorization"] = f"Bearer {login.json()['access_token']}"
    effective = await auth_client.get("/api/v1/security/effective")
    assert effective.status_code == 200
    assert "reviews:read" in effective.json()["permissions"]


def test_policy_allows_permission_in_same_tenant():
    permission = Permission(name="documents-read", resource="documents", action="read")
    role = Role(name="reviewer", tenant_id="tenant-a", permissions=[permission])
    user = User(
        email="policy-a@example.com",
        username="policy-a",
        hashed_password="unused",
        full_name="Policy A",
        tenant_id="tenant-a",
        is_active=True,
        roles=[role],
    )
    decision = evaluate_permission(user, resource="documents", action="read", resource_tenant_id="tenant-a")
    assert decision.allowed is True
    assert decision.reason == "role:reviewer"


def test_policy_denies_cross_tenant_even_with_matching_role():
    permission = Permission(name="documents-read-b", resource="documents", action="read")
    role = Role(name="reviewer-b", tenant_id="tenant-a", permissions=[permission])
    user = User(
        email="policy-b@example.com",
        username="policy-b",
        hashed_password="unused",
        full_name="Policy B",
        tenant_id="tenant-a",
        is_active=True,
        roles=[role],
    )
    decision = evaluate_permission(user, resource="documents", action="read", resource_tenant_id="tenant-b")
    assert decision.allowed is False
    assert decision.reason == "tenant_boundary"
