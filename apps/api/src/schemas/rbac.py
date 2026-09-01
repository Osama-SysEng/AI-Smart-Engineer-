"""Input and output contracts for privileged RBAC administration."""
from pydantic import BaseModel, Field


class PermissionCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    resource: str = Field(..., min_length=2, max_length=100)
    action: str = Field(..., min_length=2, max_length=50)
    description: str | None = Field(default=None, max_length=1000)


class RoleCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    is_system: bool = False


class EffectivePermissions(BaseModel):
    tenant_id: str
    roles: list[str]
    permissions: list[str]
    superuser: bool
