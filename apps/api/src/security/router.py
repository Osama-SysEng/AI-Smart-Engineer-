"""Privileged RBAC administration endpoints with tenant boundary enforcement."""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models.user import Permission, Role, User
from src.db.session import get_db
from src.schemas.rbac import EffectivePermissions, PermissionCreate, RoleCreate
from src.security.audit import record_security_event
from src.security.auth import get_current_user

router = APIRouter()


def _require_security_admin(user: User) -> None:
    if not user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="security:manage permission required")


@router.get("/effective", response_model=EffectivePermissions)
async def effective_permissions(current_user: User = Depends(get_current_user)):
    """Expose the caller's effective grants for client-side capability discovery."""
    permissions = sorted({f"{permission.resource}:{permission.action}" for role in current_user.roles for permission in role.permissions})
    return EffectivePermissions(
        tenant_id=current_user.tenant_id,
        roles=sorted(role.name for role in current_user.roles),
        permissions=permissions,
        superuser=current_user.is_superuser,
    )


@router.post("/permissions", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_permission(
    payload: PermissionCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_security_admin(current_user)
    existing = await db.execute(select(Permission).where(Permission.name == payload.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Permission name already exists")
    permission = Permission(**payload.model_dump())
    db.add(permission)
    await record_security_event(db, action="rbac.permission.create", user_id=current_user.id, outcome="success", request=request, metadata={"name": payload.name})
    await db.commit()
    return {"id": permission.id, "name": permission.name}


@router.post("/roles", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_role(
    payload: RoleCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_security_admin(current_user)
    existing = await db.execute(select(Role).where(Role.tenant_id == current_user.tenant_id, Role.name == payload.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Role name already exists in tenant")
    role = Role(**payload.model_dump(), tenant_id=current_user.tenant_id)
    db.add(role)
    await record_security_event(db, action="rbac.role.create", user_id=current_user.id, outcome="success", request=request, metadata={"name": role.name, "tenant_id": role.tenant_id})
    await db.commit()
    return {"id": role.id, "name": role.name, "tenant_id": role.tenant_id}


@router.post("/roles/{role_id}/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def grant_permission_to_role(
    role_id: str,
    permission_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_security_admin(current_user)
    role_result = await db.execute(select(Role).options(selectinload(Role.permissions)).where(Role.id == role_id, Role.tenant_id == current_user.tenant_id))
    role = role_result.scalar_one_or_none()
    permission = await db.get(Permission, permission_id)
    if not role or not permission:
        raise HTTPException(status_code=404, detail="Role or permission not found")
    if permission not in role.permissions:
        role.permissions.append(permission)
    await record_security_event(db, action="rbac.role.grant_permission", user_id=current_user.id, outcome="success", request=request, metadata={"role_id": role_id, "permission_id": permission_id})
    await db.commit()


@router.post("/users/{user_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def grant_role_to_user(
    user_id: str,
    role_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_security_admin(current_user)
    user_result = await db.execute(select(User).options(selectinload(User.roles)).where(User.id == user_id, User.tenant_id == current_user.tenant_id))
    target = user_result.scalar_one_or_none()
    role = await db.get(Role, role_id)
    if not target or not role or role.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="User or role not found in tenant")
    if role not in target.roles:
        target.roles.append(role)
    await record_security_event(db, action="rbac.user.grant_role", user_id=current_user.id, outcome="success", request=request, metadata={"target_user_id": target.id, "role_id": role_id})
    await db.commit()
