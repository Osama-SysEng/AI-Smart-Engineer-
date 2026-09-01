"""Pytest configuration for isolated integration tests."""
import asyncio
import os
import sys
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:////tmp/ai-smart-engineer-test.db"
os.environ["STORAGE_TYPE"] = "local"
os.environ["STORAGE_PATH"] = "/tmp/ai-smart-engineer-test-storage"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.db.base import Base
from src.db.models import auth_session, user, project, document, extraction, reconciliation, workflow, audit, ai, cost, engineering, notification, procurement, quality, sap, validation  # noqa: F401
from src.core.config import get_settings
from src.ai.llm_provider import LLMResponse, LLMRouter

settings = get_settings()
TEST_DATABASE_URL = settings.async_database_url
engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True)
def mock_llm(monkeypatch):
    async def fake_route(self, messages, **kwargs):
        user_message = next((m["content"] for m in reversed(messages) if m.get("role") == "user"), "")
        if "intent classifier" in messages[0].get("content", ""):
            content = '{"intent":"general_question","confidence":0.9,"entities":{"question":"Hello"},"complexity":"low","sensitivity":"low"}'
        else:
            content = f"Verified test response for: {user_message[:120]}"
        return LLMResponse(content, "test-model", "test", 10, 10, 1, 0.0)
    monkeypatch.setattr(LLMRouter, "route", fake_route)


@pytest.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def auth_client(client):
    response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "full_name": "Test User",
    })
    if response.status_code == 400:
        pass

    async with TestingSessionLocal() as db:
        from sqlalchemy import select
        from src.db.models.user import User
        result = await db.execute(select(User).where(User.username == "testuser"))
        user = result.scalar_one()
        user.is_superuser = True
        await db.commit()

    response = await client.post("/api/v1/auth/login", json={
        "username": "testuser",
        "password": "testpass123",
    })
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    yield client
