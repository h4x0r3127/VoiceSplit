import uuid
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import decode_token
from app.database import get_db
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.services.storage.base import StorageService
from app.services.storage.minio import MinioStorageService
from app.services.billing.base import BillingService
from app.services.billing.stripe_stub import StripeStubService

bearer_scheme = HTTPBearer()
_user_repo = UserRepository()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = decode_token(credentials.credentials)
    user_id_str: Optional[str] = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = await _user_repo.get_by_id(db, user_id)
    if not user or user.deleted_at is not None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    return user


def get_storage() -> StorageService:
    return MinioStorageService()


def get_billing() -> BillingService:
    return StripeStubService()
