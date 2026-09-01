"""Document tests."""
import pytest
from httpx import AsyncClient


class TestDocuments:
    async def test_list_documents(self, auth_client: AsyncClient):
        response = await auth_client.get("/api/v1/documents")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_upload_document_unauthorized(self, client: AsyncClient):
        response = await client.post("/api/v1/documents/upload")
        assert response.status_code == 401
