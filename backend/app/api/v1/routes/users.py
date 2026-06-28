from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.repositories.job_repo import JobRepository
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserAnalytics, UserResponse, UserUpdate
from sqlalchemy import func, select

router = APIRouter(prefix="/users", tags=["users"])
_user_repo = UserRepository()
_job_repo = JobRepository()


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_me(
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    if payload.name is not None:
        current_user.name = payload.name.strip()
    if payload.avatar_url is not None:
        current_user.avatar_url = payload.avatar_url
    updated = await _user_repo.update(db, current_user)
    return UserResponse.model_validate(updated)


@router.get("/me/analytics", response_model=UserAnalytics)
async def get_my_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserAnalytics:
    from app.models.job import Job, JobStatus
    from sqlalchemy import and_

    result = await db.execute(
        select(
            func.count(Job.id).label("total_jobs"),
            func.count(Job.id).filter(Job.status == JobStatus.COMPLETED).label("completed_jobs"),
            func.coalesce(func.sum(Job.duration_seconds), 0).label("total_seconds"),
        ).where(
            and_(Job.user_id == current_user.id, Job.deleted_at.is_(None))
        )
    )
    row = result.one()

    from app.models.speaker import Speaker
    speaker_result = await db.execute(
        select(func.count(Speaker.id)).join(Job).where(
            and_(Job.user_id == current_user.id, Job.deleted_at.is_(None))
        )
    )
    total_speakers = speaker_result.scalar_one()

    return UserAnalytics(
        total_jobs=row.total_jobs,
        completed_jobs=row.completed_jobs,
        total_minutes_processed=round((row.total_seconds or 0) / 60, 1),
        total_speakers_found=total_speakers,
        storage_used_bytes=current_user.storage_used_bytes,
    )
