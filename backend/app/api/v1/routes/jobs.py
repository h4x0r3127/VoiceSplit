import io
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_storage
from app.config import settings
from app.database import get_db
from app.models.job import Job, JobStatus
from app.models.user import User
from app.repositories.job_repo import JobRepository
from app.repositories.user_repo import UserRepository
from app.schemas.job import JobListResponse, JobResponse, JobStatusResponse
from app.services.storage.base import StorageService
from app.utils.logging import get_logger

router = APIRouter(prefix="/jobs", tags=["jobs"])
_job_repo = JobRepository()
_user_repo = UserRepository()
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# POST /jobs/upload
# ---------------------------------------------------------------------------

@router.post("/upload", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def upload_audio(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    storage: StorageService = Depends(get_storage),
) -> JobResponse:
    """
    Upload an audio file, persist it to MinIO, create a Job record,
    and enqueue the background processing task.
    """
    extension = (file.filename or "").rsplit(".", 1)[-1].lower()
    if extension not in settings.ALLOWED_AUDIO_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Unsupported format '{extension}'. "
                f"Allowed: {', '.join(settings.ALLOWED_AUDIO_FORMATS)}"
            ),
        )

    content = await file.read()
    size_bytes = len(content)
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    if size_bytes > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB} MB",
        )

    if size_bytes == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uploaded file is empty",
        )

    # Upload to object storage
    s3_key = f"uploads/{current_user.id}/{uuid.uuid4()}.{extension}"
    content_type = file.content_type or f"audio/{extension}"
    await storage.upload_file(s3_key, io.BytesIO(content), size_bytes, content_type)

    # Create job record
    job = Job(
        user_id=current_user.id,
        original_filename=file.filename or f"upload.{extension}",
        original_s3_key=s3_key,
        file_size_bytes=size_bytes,
        status=JobStatus.UPLOADED,
        progress=0,
    )
    created = await _job_repo.create(db, job)
    created = await _job_repo.get_by_id_with_speakers(db, created.id)

    # Update user storage usage
    await _user_repo.update_storage_used(db, current_user.id, size_bytes)

    # Enqueue background processing task
    try:
        from app.workers.tasks.process_audio import process_audio_task
        process_audio_task.apply_async(
            kwargs={"job_id": str(created.id), "s3_key": s3_key},
            queue="audio_processing",
        )
        logger.info("task_enqueued", job_id=str(created.id), s3_key=s3_key)
    except Exception as exc:
        # Non-fatal: job is created but processing won't start automatically.
        # The operator can retry manually or via a management command.
        logger.error("task_enqueue_failed", job_id=str(created.id), error=str(exc))

    await db.refresh(created, attribute_names=["speakers"])
    return JobResponse.model_validate(created)


# ---------------------------------------------------------------------------
# GET /jobs
# ---------------------------------------------------------------------------

@router.get("", response_model=JobListResponse)
async def list_jobs(
    page: int = 1,
    per_page: int = 20,
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobListResponse:
    """List all jobs for the authenticated user with optional status filter."""
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


# ---------------------------------------------------------------------------
# GET /jobs/{job_id}
# ---------------------------------------------------------------------------

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobResponse:
    """Get a single job with all its speaker data."""
    job = await _job_repo.get_by_id_with_speakers(db, job_id)
    _assert_job_access(job, current_user)
    return JobResponse.model_validate(job)


# ---------------------------------------------------------------------------
# GET /jobs/{job_id}/status  — lightweight polling endpoint
# ---------------------------------------------------------------------------

@router.get("/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobStatusResponse:
    """
    Lightweight endpoint to poll job progress.
    Clients that cannot use WebSockets may poll this every few seconds.
    """
    job = await _job_repo.get_by_id(db, job_id)
    _assert_job_access(job, current_user)
    return JobStatusResponse(
        job_id=str(job.id),
        status=job.status,
        pipeline_stage=job.pipeline_stage,
        progress=job.progress,
        error_message=job.error_message,
        duration_seconds=job.duration_seconds,
        audio_metadata=job.audio_metadata,
    )


# ---------------------------------------------------------------------------
# GET /jobs/{job_id}/download  — presigned download URL
# ---------------------------------------------------------------------------

@router.get("/{job_id}/download")
async def get_job_download_url(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    storage: StorageService = Depends(get_storage),
) -> dict:
    """
    Generate a time-limited presigned download URL for the original uploaded file.
    The processed/separated file URL is generated from export records (Phase 4).
    """
    job = await _job_repo.get_by_id(db, job_id)
    _assert_job_access(job, current_user)

    url = await storage.get_presigned_url(job.original_s3_key, expires_seconds=3600)
    return {"download_url": url, "expires_in": 3600}


# ---------------------------------------------------------------------------
# DELETE /jobs/{job_id}
# ---------------------------------------------------------------------------

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    storage: StorageService = Depends(get_storage),
) -> None:
    """Soft-delete a job record. The S3 file is retained for 7 days (cleaned by a Phase 5 worker)."""
    job = await _job_repo.get_by_id(db, job_id)
    _assert_job_access(job, current_user)
    await _job_repo.soft_delete(db, job_id)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _assert_job_access(job: Optional[Job], user: User) -> None:
    if not job or job.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    if job.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
