import uuid
from datetime import datetime, timezone
from typing import Generic, List, Optional, Type, TypeVar

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]) -> None:
        self._model = model

    async def get_by_id(self, db: AsyncSession, record_id: uuid.UUID) -> Optional[ModelType]:
        result = await db.execute(
            select(self._model).where(
                self._model.id == record_id,
                self._model.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 50,
    ) -> List[ModelType]:
        result = await db.execute(
            select(self._model)
            .where(self._model.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, obj: ModelType) -> ModelType:
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    async def update(self, db: AsyncSession, obj: ModelType) -> ModelType:
        await db.flush()
        await db.refresh(obj)
        return obj

    async def soft_delete(self, db: AsyncSession, record_id: uuid.UUID) -> bool:
        obj = await self.get_by_id(db, record_id)
        if obj is None:
            return False
        obj.deleted_at = datetime.now(timezone.utc)
        await db.flush()
        return True
