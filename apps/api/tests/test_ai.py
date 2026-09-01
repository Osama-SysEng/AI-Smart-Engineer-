"""AI tests."""
import pytest
from httpx import AsyncClient


class TestAI:
    async def test_chat(self, auth_client: AsyncClient):
        response = await auth_client.post("/api/v1/ai/chat", json={
            "message": "Hello",
            "context": {},
        })
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "trace_id" in data

    async def test_list_providers(self, auth_client: AsyncClient):
        response = await auth_client.get("/api/v1/ai/providers")
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        assert len(data["providers"]) > 0
