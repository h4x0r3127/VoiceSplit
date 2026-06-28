import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_storage
from app.config import settings
from app.database import get_db
from app.models.job import Job, JobStatus
from app.models.user import User
from app.repositories.job_repo import JobRepository
from app.schemas.job import JobListResponse, JobResponse
from app.services.storage.base import StorageService

router = APIRouter(prefix="/jobs", tags=["jobs"])
_job_repo = JobRepository()

_AUDIO_CONTENT_TYPES = {
    "audio/mpeg",
    "audio/mp3",
    "audio/wav",
    "audio/x-wav",
    "audio/aac",
    "audio/x-aac",
    "audio/mp4",
    "audio/x-m4a",
    "audio/flac",
    "audio/x-flac",
    "audio/ogg",
    "audio/vorbis",
}


@router.post("/upload", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def upload_audio(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    storage: StorageService = Depends(get_storage),
) -> JobResponse:
    extension = (file.filename or "").rsplit(".", 1)[-1].lower()
    if extension not in settings.ALLOWED_AUDIO_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported format '{extension}'. Allowed: {', '.join(settings.ALLOWED_AUDIO_FORMATS)}",
        )

    content = await file.read()
    size_bytes = len(content)
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    if size_bytes > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB} MB",
        )

    s3_key = f"uploads/{current_user.id}/{uuid.uuid4()}.{extension}"
    import io
    await storage.upload_file(s3_key, io.BytesIO(content), size_bytes, file.content_type or "audio/mpeg")

    job = Job(
        user_id=current_user.id,
        original_filename=file.filename or f"upload.{extension}",
        original_s3_key=s3_key,
        file_size_bytes=size_bytes,
        status=JobStatus.UPLOADED,
        progress=0,
    )
    created = await _job_repo.create(db, job)
    return JobResponse.model_validate(created)


@router.get("", response_model=JobListResponse)
async def list_jobs(
    page: int = 1,
    per_page: int = 20,
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobListResponse:
    job_status = None
    if status_filter:
        try:
            job_status = JobStatus(status_filter.upper())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status filter: {status_filter}",
            )

    jobs, total = await _job_repo.get_jobs_by_user(
        db, current_user.id, page=page, per_page=per_page, status_filter=job_status
    )
    return JobListResponse(
        items=[JobResponse.model_validate(j) for j in jobs],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobResponse:
    job = await _job_repo.get_by_id_with_speakers(db, job_id)
    _assert_job_access(job, current_user)
    return JobResponse.model_validate(job)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    job = await _job_repo.get_by_id(db, job_id)
    _assert_job_access(job, current_user)
    await _job_repo.soft_delete(db, job_id)


def _assert_job_access(job: Optional[Job], user: User) -> None:
    if not job or job.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    if job.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
