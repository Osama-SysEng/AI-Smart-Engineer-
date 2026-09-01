"""Authentication utilities."""
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.core.config import get_settings
from src.core.logging import get_logger
from src.db.session import get_db
from src.db.models.auth_session import AuthSession
from src.db.models.user import Role, User

logger = get_logger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security_scheme = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    settings = get_settings()
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc), "type": "access", "jti": str(uuid4())})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict, refresh_jti: str | None = None) -> str:
    settings = get_settings()
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc), "type": "refresh", "jti": refresh_jti or str(uuid4())})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.username == username, User.is_deleted == False))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    settings = get_settings()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None or payload.get("type") == "refresh":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    session_id = payload.get("sid")
    if settings.REQUIRE_SESSION_BOUND_TOKENS:
        if not session_id:
            raise credentials_exception
        session_result = await db.execute(select(AuthSession).where(AuthSession.id == session_id))
        auth_session = session_result.scalar_one_or_none()
        expires_at = auth_session.expires_at if auth_session else None
        if expires_at and expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if not auth_session or auth_session.user_id != user_id or auth_session.revoked_at or (expires_at and expires_at <= datetime.now(timezone.utc)):
            raise credentials_exception

    result = await db.execute(
        select(User)
        .options(selectinload(User.roles).selectinload(Role.permissions))
        .where(User.id == user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user



def decode_access_token(token: str) -> dict:
    settings = get_settings()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") == "refresh" or not payload.get("sub"):
            raise credentials_exception
        return payload
    except JWTError as exc:
        raise credentials_exception from exc

def require_permissions(*permissions: str):
    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        user_permissions = set()
        for role in current_user.roles:
            for perm in role.permissions:
                user_permissions.add(f"{perm.resource}:{perm.action}")

        for required in permissions:
            if required not in user_permissions and not current_user.is_superuser:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {required} required"
                )
        return current_user
    return permission_checker
