import secrets
import uuid
from datetime import timedelta

import redis.asyncio as aioredis
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_google_token,
)
from app.core.security import hash_password, verify_password
from app.database import get_db
from app.models.user import AuthProvider, User
from app.repositories.user_repo import UserRepository
from app.schemas.auth import (
    ForgotPasswordRequest,
    GoogleAuthRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserInToken,
)

router = APIRouter(prefix="/auth", tags=["auth"])
_user_repo = UserRepository()

RESET_TOKEN_TTL = 3600  # seconds


def _build_token_response(user: User) -> TokenResponse:
    subject = str(user.id)
    access_token = create_access_token({"sub": subject})
    refresh_token = create_refresh_token({"sub": subject})
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserInToken(
            id=str(user.id),
            email=user.email,
            name=user.name,
            avatar_url=user.avatar_url,
            credits=user.credits,
        ),
    )


async def _get_redis() -> aioredis.Redis:
    return aioredis.from_url(settings.REDIS_URL, decode_responses=True)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    existing = await _user_repo.get_by_email(db, payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )
    user = User(
        email=payload.email,
        name=payload.name,
        password_hash=hash_password(payload.password),
        provider=AuthProvider.EMAIL,
        is_verified=False,
        is_active=True,
    )
    created = await _user_repo.create(db, user)
    return _build_token_response(created)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    user = await _user_repo.get_by_email(db, payload.email)
    if not user or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )
    return _build_token_response(user)


@router.post("/google", response_model=TokenResponse)
async def google_auth(payload: GoogleAuthRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth is not configured",
        )
    google_data = verify_google_token(payload.id_token, settings.GOOGLE_CLIENT_ID)

    user = await _user_repo.get_by_provider_id(db, "google", google_data["provider_id"])
    if not user:
        user = await _user_repo.get_by_email(db, google_data["email"])

    if user:
        if user.provider == AuthProvider.EMAIL:
            user.provider_id = google_data["provider_id"]
            user.avatar_url = user.avatar_url or google_data.get("avatar_url")
            await _user_repo.update(db, user)
    else:
        user = User(
            email=google_data["email"],
            name=google_data["name"] or google_data["email"].split("@")[0],
            avatar_url=google_data.get("avatar_url"),
            provider=AuthProvider.GOOGLE,
            provider_id=google_data["provider_id"],
            is_verified=google_data.get("email_verified", False),
            is_active=True,
        )
        user = await _user_repo.create(db, user)

    return _build_token_response(user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(payload: RefreshRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    token_data = decode_token(payload.refresh_token)
    if token_data.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    redis = await _get_redis()
    revoked = await redis.get(f"revoked_refresh:{payload.refresh_token}")
    if revoked:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token has been revoked")

    user_id = uuid.UUID(token_data["sub"])
    user = await _user_repo.get_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    await redis.setex(
        f"revoked_refresh:{payload.refresh_token}",
        settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        "1",
    )
    return _build_token_response(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: RefreshRequest) -> None:
    redis = await _get_redis()
    await redis.setex(
        f"revoked_refresh:{payload.refresh_token}",
        settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        "1",
    )


@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
async def forgot_password(
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> dict:
    user = await _user_repo.get_by_email(db, payload.email)
    if user:
        token = secrets.token_urlsafe(32)
        redis = await _get_redis()
        await redis.setex(f"pw_reset:{token}", RESET_TOKEN_TTL, str(user.id))
        background_tasks.add_task(_log_reset_token, user.email, token)
    return {"message": "If that email is registered, a reset link has been sent"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    payload: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    redis = await _get_redis()
    user_id_str = await redis.get(f"pw_reset:{payload.token}")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )
    user = await _user_repo.get_by_id(db, uuid.UUID(user_id_str))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.password_hash = hash_password(payload.new_password)
    await _user_repo.update(db, user)
    await redis.delete(f"pw_reset:{payload.token}")
    return {"message": "Password updated successfully"}


def _log_reset_token(email: str, token: str) -> None:
    from app.utils.logging import get_logger
    logger = get_logger(__name__)
    logger.info("password_reset_requested", email=email, token_preview=token[:8] + "...")
