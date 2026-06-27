import uuid
from typing import List, Optional, Tuple

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.job import Job, JobStatus
from app.repositories.base import BaseRepository


class JobRepository(BaseRepository[Job]):
    def __init__(self) -> None:
        super().__init__(Job)

    async def get_by_id_with_speakers(
        self, db: AsyncSession, job_id: uuid.UUID
    ) -> Optional[Job]:
        result = await db.execute(
            select(Job)
            .options(selectinload(Job.speakers))
            .where(Job.id == job_id, Job.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_jobs_by_user(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        page: int = 1,
        per_page: int = 20,
        status_filter: Optional[JobStatus] = None,
    ) -> Tuple[List[Job], int]:
        query = select(Job).where(Job.user_id == user_id, Job.deleted_at.is_(None))

        if status_filter is not None:
            query = query.where(Job.status == status_filter)

        count_result = await db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar_one()

        result = await db.execute(
            query.options(selectinload(Job.speakers))
            .order_by(Job.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        jobs = list(result.scalars().all())
        return jobs, total

    async def update_status(
        self,
        db: AsyncSession,
        job_id: uuid.UUID,
        status: JobStatus,
        stage: Optional[str] = None,
        progress: int = 0,
        message: Optional[str] = None,
    ) -> Optional[Job]:
        values: dict = {"status": status, "progress": progress}
        if stage is not None:
            values["pipeline_stage"] = stage
        if message is not None:
            values["error_message"] = message

        await db.execute(
            update(Job).where(Job.id == job_id).values(**values)
        )
        await db.flush()
        return await self.get_by_id(db, job_id)

    async def update_metadata(
        self, db: AsyncSession, job_id: uuid.UUID, metadata: dict
    ) -> Optional[Job]:
        await db.execute(
            update(Job).where(Job.id == job_id).values(audio_metadata=metadata)
        )
        await db.flush()
        return await self.get_by_id(db, job_id)
