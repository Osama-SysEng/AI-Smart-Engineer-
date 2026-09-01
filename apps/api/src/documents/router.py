"""Documents router."""
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from src.db.session import get_db
from src.db.models.document import Document, DocumentVersion, ExtractedEntity
from src.db.models.user import User
from src.security.auth import get_current_user, require_permissions
from src.schemas.document import DocumentResponse, ExtractedEntityResponse
from src.storage.service import StorageService
from src.queue.tasks import process_document_task
from src.core.logging import get_logger
from src.core.config import get_settings
from src.db.models.project import Project
from pathlib import Path

logger = get_logger(__name__)
router = APIRouter()
storage_service = StorageService()


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    project_id: str = Form(...),
    site_id: str | None = Form(None),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload and process a document."""
    # Validate project ownership before accepting file
    project_result = await db.execute(select(Project).where(Project.id == project_id, Project.tenant_id == current_user.tenant_id, Project.is_deleted == False))
    if not project_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    allowed_extensions = {e.lower() for e in get_settings().ALLOWED_EXTENSIONS}
    filename = file.filename or "upload"
    ext = Path(filename).suffix.lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"File type not allowed: {ext}")

    # Save file
    doc_id = str(uuid.uuid4())
    storage_path = await storage_service.save_file(file, doc_id)

    document = Document(
        id=doc_id,
        project_id=project_id,
        site_id=site_id,
        uploaded_by=current_user.id,
        filename=storage_path.split("/")[-1],
        original_filename=file.filename,
        file_type=ext,
        file_size=Path(storage_path).stat().st_size if storage_path.startswith("/") and Path(storage_path).exists() else 0,
        mime_type=file.content_type or "application/octet-stream",
        storage_path=storage_path,
        status="uploaded",
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)

    # Queue processing
    process_document_task.delay(doc_id)

    logger.info("Document uploaded", document_id=doc_id, filename=file.filename)
    return document


@router.get("", response_model=List[DocumentResponse])
async def list_documents(
    project_id: str | None = None,
    site_id: str | None = None,
    status: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List documents with filters."""
    query = select(Document).join(Project, Project.id == Document.project_id).where(Document.is_deleted == False, Project.tenant_id == current_user.tenant_id)
    if project_id:
        query = query.where(Document.project_id == project_id)
    if site_id:
        query = query.where(Document.site_id == site_id)
    if status:
        query = query.where(Document.status == status)

    query = query.offset(skip).limit(limit).order_by(Document.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get document by ID."""
    result = await db.execute(
        select(Document).join(Project, Project.id == Document.project_id).where(Document.id == document_id, Document.is_deleted == False, Project.tenant_id == current_user.tenant_id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("/{document_id}/entities", response_model=List[ExtractedEntityResponse])
async def get_document_entities(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get extracted entities for a document."""
    result = await db.execute(
        select(ExtractedEntity).join(Document, Document.id == ExtractedEntity.document_id).join(Project, Project.id == Document.project_id).where(ExtractedEntity.document_id == document_id, Project.tenant_id == current_user.tenant_id)
    )
    return result.scalars().all()
