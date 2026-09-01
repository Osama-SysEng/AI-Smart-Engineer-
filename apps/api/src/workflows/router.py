"""Workflows router."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.db.session import get_db
from src.db.models.workflow import Workflow, WorkflowRun, Task
from src.db.models.user import User
from src.db.models.project import Project
from src.security.auth import get_current_user, require_permissions
from src.schemas.workflow import WorkflowCreate, WorkflowResponse, WorkflowRunResponse, TaskCreate, TaskResponse
from src.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    data: WorkflowCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("workflow:create"))
):
    """Create a workflow."""
    if data.project_id:
        owner = await db.execute(select(Project).where(Project.id == data.project_id, Project.tenant_id == current_user.tenant_id, Project.is_deleted == False))
        if not owner.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Project not found")
    workflow = Workflow(
        name=data.name,
        description=data.description,
        trigger_type=data.trigger_type,
        trigger_config=data.trigger_config,
        steps=data.steps,
        project_id=data.project_id,
        created_by=current_user.id,
    )
    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)
    return workflow


@router.get("", response_model=List[WorkflowResponse])
async def list_workflows(
    project_id: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List workflows."""
    query = select(Workflow).join(Project, Project.id == Workflow.project_id, isouter=True).where(Workflow.is_active == True, (Workflow.project_id.is_(None) | (Project.tenant_id == current_user.tenant_id)))
    if project_id:
        query = query.where(Workflow.project_id == project_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{workflow_id}/runs", response_model=List[WorkflowRunResponse])
async def list_workflow_runs(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List workflow runs."""
    result = await db.execute(
        select(WorkflowRun)
        .join(Workflow, Workflow.id == WorkflowRun.workflow_id)
        .join(Project, Project.id == Workflow.project_id, isouter=True)
        .where(
            WorkflowRun.workflow_id == workflow_id,
            (Workflow.project_id.is_(None) | (Project.tenant_id == current_user.tenant_id)),
        )
    )
    return result.scalars().all()


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("task:create"))
):
    """Create a task."""
    project_result = await db.execute(
        select(Project).where(
            Project.id == data.project_id,
            Project.tenant_id == current_user.tenant_id,
            Project.is_deleted == False,
        )
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    task = Task(
        project_id=data.project_id,
        site_id=data.site_id,
        title=data.title,
        description=data.description,
        priority=data.priority,
        assigned_to=data.assigned_to,
        due_date=data.due_date,
        source=data.source,
        source_id=data.source_id,
        created_by=current_user.id,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    project_id: str | None = None,
    assigned_to: str | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List tasks."""
    query = select(Task).join(Project, Project.id == Task.project_id).where(Project.tenant_id == current_user.tenant_id)
    if project_id:
        query = query.where(Task.project_id == project_id)
    if assigned_to:
        query = query.where(Task.assigned_to == assigned_to)
    if status:
        query = query.where(Task.status == status)
    result = await db.execute(query.order_by(Task.created_at.desc()))
    return result.scalars().all()
