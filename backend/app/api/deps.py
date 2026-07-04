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

    print("\n========== AUTH DEBUG ==========")

    print("TOKEN:", credentials.credentials)

    payload = decode_token(credentials.credentials)
    print("PAYLOAD:", payload)

    user_id_str = payload.get("sub")
    print("SUB:", user_id_str)

    if not user_id_str:
        print("❌ No sub in token")
        raise HTTPException(status_code=401, detail="Invalid token payload")

    try:
        user_id = uuid.UUID(user_id_str)
        print("UUID:", user_id)
    except Exception as e:
        print("UUID ERROR:", e)
        raise HTTPException(status_code=401, detail="Invalid UUID")

    user = await _user_repo.get_by_id(db, user_id)

    print("USER:", user)

    if user:
        print("ACTIVE:", user.is_active)
        print("DELETED:", user.deleted_at)

    print("================================\n")

    if not user or user.deleted_at is not None or not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="User not found or inactive",
        )

    return user


def get_storage() -> StorageService:
    return MinioStorageService()


def get_billing() -> BillingService:
    return StripeStubService()
