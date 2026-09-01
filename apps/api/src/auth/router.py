"""Authentication router with server-side session controls."""
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.db.session import get_db
from src.db.models.auth_session import AuthSession
from src.db.models.user import User
from src.security.audit import record_security_event
from src.security.auth import authenticate_user, create_access_token, create_refresh_token, decode_access_token, get_password_hash, get_current_user
from src.schemas.auth import RefreshTokenRequest, UserCreate, UserResponse, UserLogin, Token
from src.core.config import get_settings
from src.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()
security = HTTPBearer()


def _session_expiry() -> datetime:
    settings = get_settings()
    return datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)


def _token_pair(user: User, session: AuthSession) -> Token:
    settings = get_settings()
    claims = {"sub": user.id, "username": user.username, "tenant_id": user.tenant_id, "sid": session.id}
    return Token(
        access_token=create_access_token(claims),
        refresh_token=create_refresh_token(claims, session.refresh_jti),
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        session_id=session.id,
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        phone=user_data.phone,
        department_id=user_data.department_id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    logger.info("User registered", user_id=user.id, username=user.username)
    return user


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, request: Request, db: AsyncSession = Depends(get_db)):
    """Login and get tokens."""
    user = await authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is disabled")

    session = AuthSession(
        user_id=user.id,
        tenant_id=user.tenant_id,
        refresh_jti=str(uuid4()),
        expires_at=_session_expiry(),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    user.last_login = datetime.now(timezone.utc)
    db.add(session)
    await record_security_event(db, action="auth.login", user_id=user.id, outcome="success", request=request, metadata={"tenant_id": user.tenant_id})
    await db.commit()
    await db.refresh(session)
    logger.info("User logged in", user_id=user.id, session_id=session.id)
    return _token_pair(user, session)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info."""
    return current_user


@router.post("/refresh", response_model=Token)
async def refresh_token(payload: RefreshTokenRequest, request: Request, db: AsyncSession = Depends(get_db)):
    """Rotate a refresh token and revoke the session if replay is detected."""
    from jose import JWTError, jwt

    settings = get_settings()
    try:
        claims = jwt.decode(payload.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if claims.get("type") != "refresh" or not claims.get("sub") or not claims.get("sid") or not claims.get("jti"):
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid refresh token") from exc

    session_result = await db.execute(select(AuthSession).where(AuthSession.id == claims["sid"]))
    session = session_result.scalar_one_or_none()
    expires_at = session.expires_at if session else None
    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if not session or session.user_id != claims["sub"] or session.revoked_at or (expires_at and expires_at <= datetime.now(timezone.utc)):
        raise HTTPException(status_code=401, detail="Session is not active")
    if session.refresh_jti != claims["jti"]:
        session.revoked_at = datetime.now(timezone.utc)
        session.revoke_reason = "refresh_replay_detected"
        await record_security_event(db, action="auth.refresh", user_id=session.user_id, outcome="refresh_replay_detected", request=request)
        await db.commit()
        raise HTTPException(status_code=401, detail="Refresh token replay detected")

    result = await db.execute(select(User).where(User.id == session.user_id, User.is_deleted == False))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found")
    session.refresh_jti = str(uuid4())
    await record_security_event(db, action="auth.refresh", user_id=user.id, outcome="success", request=request, metadata={"session_id": session.id})
    await db.commit()
    await db.refresh(session)
    return _token_pair(user, session)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: Request, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Revoke the current server-side session without deleting audit evidence."""
    token = request.headers.get("authorization", "").removeprefix("Bearer ")
    claims = decode_access_token(token)
    session_id = claims.get("sid")
    if session_id:
        result = await db.execute(select(AuthSession).where(AuthSession.id == session_id, AuthSession.user_id == current_user.id))
        session = result.scalar_one_or_none()
        if session and not session.revoked_at:
            session.revoked_at = datetime.now(timezone.utc)
            session.revoke_reason = "user_logout"
    await record_security_event(db, action="auth.logout", user_id=current_user.id, outcome="success", request=request)
    await db.commit()
