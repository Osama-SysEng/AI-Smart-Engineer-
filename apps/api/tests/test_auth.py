"""Auth tests."""
import pytest
from httpx import AsyncClient


class TestAuth:
    async def test_register(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/register", json={
            "email": "new@example.com",
            "username": "newuser",
            "password": "newpass123",
            "full_name": "New User",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "new@example.com"
        assert data["username"] == "newuser"

    async def test_login(self, client: AsyncClient):
        # First register
        await client.post("/api/v1/auth/register", json={
            "email": "login@example.com",
            "username": "loginuser",
            "password": "loginpass123",
            "full_name": "Login User",
        })

        response = await client.post("/api/v1/auth/login", json={
            "username": "loginuser",
            "password": "loginpass123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_login_invalid(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/login", json={
            "username": "nonexistent",
            "password": "wrong",
        })
        assert response.status_code == 401

    async def test_get_me_unauthorized(self, client: AsyncClient):
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401
