import uuid
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.speaker import Speaker
from app.repositories.base import BaseRepository


class SpeakerRepository(BaseRepository[Speaker]):
    def __init__(self) -> None:
        super().__init__(Speaker)

    async def get_by_job(self, db: AsyncSession, job_id: uuid.UUID) -> List[Speaker]:
        result = await db.execute(
            select(Speaker)
            .where(Speaker.job_id == job_id, Speaker.deleted_at.is_(None))
            .order_by(Speaker.created_at.asc())
        )
        return list(result.scalars().all())

    async def create_bulk(
        self, db: AsyncSession, speakers: List[Speaker]
    ) -> List[Speaker]:
        for speaker in speakers:
            db.add(speaker)
        await db.flush()
        for speaker in speakers:
            await db.refresh(speaker)
        return speakers
