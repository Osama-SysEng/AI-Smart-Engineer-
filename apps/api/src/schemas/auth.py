"""Authentication schemas."""
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: str | None = None
    department_id: str | None = None


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: str
    phone: str | None
    department_id: str | None
    is_active: bool
    is_superuser: bool
    mfa_enabled: bool
    last_login: str | None
    tenant_id: str

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str
    mfa_code: str | None = None


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    session_id: str | None = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=20)


class TokenData(BaseModel):
    user_id: str | None = None
    username: str | None = None
    scopes: list[str] = []
