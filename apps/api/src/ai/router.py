"""AI Chat router."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.db.session import get_db
from src.db.models.user import User
from src.db.models.project import Project, Site
from src.security.auth import get_current_user, require_permissions, decode_access_token
from src.schemas.ai import AIChatRequest, AIChatResponse, AIUsageResponse
from src.agents.orchestrator import AgentOrchestrator
from src.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()
orchestrator = AgentOrchestrator()


@router.post("/chat", response_model=AIChatResponse)
async def ai_chat(
    request: AIChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI Engineering Assistant chat."""
    if request.project_id:
        result = await db.execute(select(Project).where(Project.id == request.project_id, Project.tenant_id == current_user.tenant_id, Project.is_deleted == False))
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Project not found")
    if request.site_id:
        result = await db.execute(select(Site).join(Project, Project.id == Site.project_id).where(Site.id == request.site_id, Project.tenant_id == current_user.tenant_id, Site.is_deleted == False))
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Site not found")

    try:
        result = await orchestrator.process_request(
            message=request.message,
            user_id=current_user.id,
            context=request.context,
            project_id=request.project_id,
            site_id=request.site_id,
            model_override=request.model_override,
        )
        return AIChatResponse(**result)
    except Exception as e:
        logger.error("AI chat error", error=str(e), user_id=current_user.id)
        raise HTTPException(status_code=500, detail="AI request failed")


@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket for real-time AI chat."""
    token = websocket.query_params.get("access_token")
    if not token:
        await websocket.close(code=1008)
        return
    try:
        payload = decode_access_token(token)
        user_id = payload["sub"]
        async with __import__("src.db.session", fromlist=["async_session"]).async_session() as db:
            result = await db.execute(select(User).where(User.id == user_id, User.is_deleted == False, User.is_active == True))
            current_user = result.scalar_one_or_none()
            if current_user is None:
                await websocket.close(code=1008)
                return
    except HTTPException:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            message = str(data.get("message", "")).strip()
            if not message or len(message) > 20000:
                await websocket.send_json({"error": "Invalid message"})
                continue
            project_id = data.get("project_id")
            site_id = data.get("site_id")
            if project_id:
                project_result = await db.execute(select(Project).where(Project.id == project_id, Project.tenant_id == current_user.tenant_id, Project.is_deleted == False))
                if not project_result.scalar_one_or_none():
                    await websocket.send_json({"error": "Project not found"})
                    continue
            if site_id:
                site_result = await db.execute(select(Site).join(Project, Project.id == Site.project_id).where(Site.id == site_id, Project.tenant_id == current_user.tenant_id, Site.is_deleted == False))
                if not site_result.scalar_one_or_none():
                    await websocket.send_json({"error": "Site not found"})
                    continue
            result = await orchestrator.process_request(
                message=message,
                user_id=user_id,
                context=data.get("context") or {},
                project_id=data.get("project_id"),
                site_id=data.get("site_id"),
                model_override=data.get("model_override"),
            )
            await websocket.send_json(result)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error("WebSocket error", error=str(e))
        await websocket.close()


@router.get("/usage", response_model=List[AIUsageResponse])
async def get_ai_usage(
    period: str = "daily",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("ai:admin"))
):
    """Get AI usage statistics."""
    from sqlalchemy import select
    from src.db.models.ai import AIUsage

    result = await db.execute(
        select(AIUsage).where(AIUsage.period == period).order_by(AIUsage.created_at.desc())
    )
    return result.scalars().all()


@router.get("/providers")
async def list_ai_providers(
    current_user: User = Depends(get_current_user)
):
    """List available AI providers."""
    return {
        "providers": [
            {"id": "openai", "name": "OpenAI", "models": ["gpt-4o", "gpt-4o-mini"]},
            {"id": "anthropic", "name": "Anthropic", "models": ["claude-3-5-sonnet", "claude-3-haiku"]},
            {"id": "google", "name": "Google", "models": ["gemini-1.5-pro", "gemini-1.5-flash"]},
            {"id": "deepseek", "name": "DeepSeek", "models": ["deepseek-chat", "deepseek-coder"]},
            {"id": "local", "name": "Local (Ollama)", "models": ["llama3", "mistral", "codellama"]},
        ]
    }
