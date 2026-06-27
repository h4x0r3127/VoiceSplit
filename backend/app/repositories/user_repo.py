import uuid
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self) -> None:
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        result = await db.execute(
            select(User).where(User.email == email, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_provider_id(
        self,
        db: AsyncSession,
        provider: str,
        provider_id: str,
    ) -> Optional[User]:
        from app.models.user import AuthProvider

        result = await db.execute(
            select(User).where(
                User.provider == AuthProvider(provider),
                User.provider_id == provider_id,
                User.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def update_storage_used(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        bytes_delta: int,
    ) -> None:
        await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(storage_used_bytes=User.storage_used_bytes + bytes_delta)
        )
        await db.flush()
