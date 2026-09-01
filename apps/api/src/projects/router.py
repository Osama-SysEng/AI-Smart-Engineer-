"""Projects router."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from src.db.session import get_db
from src.db.models.project import Project, Site, Department
from src.db.models.user import User
from src.security.auth import get_current_user, require_permissions
from src.schemas.project import ProjectCreate, ProjectResponse, SiteCreate, SiteResponse, DepartmentCreate, DepartmentResponse
from src.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


def project_response(project: Project, include_relations: bool = True) -> ProjectResponse:
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        client=project.client,
        location=project.location,
        status=project.status,
        start_date=project.start_date,
        end_date=project.end_date,
        budget=project.budget,
        currency=project.currency,
        health_score=project.health_score,
        tenant_id=project.tenant_id,
        created_at=project.created_at,
        sites=[SiteResponse.model_validate(site) for site in project.sites] if include_relations else [],
        departments=[DepartmentResponse.model_validate(department) for department in project.departments] if include_relations else [],
    )


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("project:create"))
):
    """Create a new project."""
    project = Project(
        name=project_data.name,
        description=project_data.description,
        client=project_data.client,
        location=project_data.location,
        start_date=project_data.start_date,
        end_date=project_data.end_date,
        budget=project_data.budget,
        currency=project_data.currency,
        metadata_payload=project_data.metadata,
        tenant_id=current_user.tenant_id,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    logger.info("Project created", project_id=project.id, name=project.name)
    return project_response(project, include_relations=False)


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List projects with pagination."""
    query = select(Project).options(selectinload(Project.sites), selectinload(Project.departments)).where(
        and_(Project.tenant_id == current_user.tenant_id, Project.is_deleted == False)
    )
    if status:
        query = query.where(Project.status == status)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return [project_response(project) for project in result.scalars().all()]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get project by ID."""
    result = await db.execute(
        select(Project).options(selectinload(Project.sites), selectinload(Project.departments)).where(
            Project.id == project_id,
            Project.tenant_id == current_user.tenant_id,
            Project.is_deleted == False
        )
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project_response(project)


@router.post("/{project_id}/sites", response_model=SiteResponse, status_code=status.HTTP_201_CREATED)
async def create_site(
    project_id: str,
    site_data: SiteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("project:update"))
):
    """Create a site under a project."""
    result = await db.execute(select(Project).where(Project.id == project_id, Project.tenant_id == current_user.tenant_id, Project.is_deleted == False))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    site = Site(
        project_id=project_id,
        name=site_data.name,
        code=site_data.code,
        location=site_data.location,
        status=site_data.status,
        manager_id=site_data.manager_id,
        metadata_payload=site_data.metadata,
    )
    db.add(site)
    await db.commit()
    await db.refresh(site)
    return site


@router.get("/{project_id}/sites", response_model=List[SiteResponse])
async def list_sites(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List sites for a project."""
    result = await db.execute(
        select(Site).join(Project, Project.id == Site.project_id).where(Site.project_id == project_id, Project.tenant_id == current_user.tenant_id, Site.is_deleted == False)
    )
    return result.scalars().all()


@router.post("/{project_id}/departments", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    project_id: str,
    dept_data: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("project:update"))
):
    """Create a department under a project."""
    result = await db.execute(select(Project).where(Project.id == project_id, Project.tenant_id == current_user.tenant_id, Project.is_deleted == False))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    dept = Department(
        project_id=project_id,
        name=dept_data.name,
        code=dept_data.code,
        description=dept_data.description,
        head_id=dept_data.head_id,
    )
    db.add(dept)
    await db.commit()
    await db.refresh(dept)
    return dept
