"""Project tests."""
import pytest
from httpx import AsyncClient


class TestProjects:
    async def test_create_project(self, auth_client: AsyncClient):
        response = await auth_client.post("/api/v1/projects", json={
            "name": "Test Project",
            "description": "Test Description",
            "client": "Test Client",
            "location": "Test Location",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Project"
        assert data["status"] == "active"

    async def test_list_projects(self, auth_client: AsyncClient):
        response = await auth_client.get("/api/v1/projects")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_create_project_unauthorized(self, client: AsyncClient):
        response = await client.post("/api/v1/projects", json={
            "name": "Test Project",
        })
        assert response.status_code == 401
