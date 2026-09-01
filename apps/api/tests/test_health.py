"""Health tests."""
import pytest
from httpx import AsyncClient


class TestHealth:
    async def test_health(self, client: AsyncClient):
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    async def test_ready(self, client: AsyncClient):
        response = await client.get("/api/v1/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert "database" in data

    async def test_live(self, client: AsyncClient):
        response = await client.get("/api/v1/health/live")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"
