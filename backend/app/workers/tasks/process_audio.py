"""
Background task: process_audio_task

This task handles the non-AI pipeline stages for Phase 3:

  UPLOADED → PREPROCESSING (validate + extract metadata) → COMPLETED

When the AI pipeline is activated in Phase 4, the status progression will
expand to: PREPROCESSING → VAD → DIARIZING → EMBEDDING → CLUSTERING →
SEPARATING → TRANSCRIBING → ANALYZING → RECONSTRUCTING → COMPLETED.

Progress events are published to a Redis pub/sub channel so WebSocket
connections can forward them to the browser in real time.
"""
from __future__ import annotations

import asyncio
import json
import os
import tempfile
import uuid
from typing import Any

from celery import Task
from celery.utils.log import get_task_logger

from app.workers.celery_app import celery_app
from app.config import settings
from pathlib import Path

from ai.preprocessing.service import PreprocessingService
from ai.preprocessing.models import AudioInput
from ai.interfaces.base_stage import StageContext

logger = get_task_logger(__name__)

# Redis pub/sub channel pattern: "job_progress:<job_id>"
PROGRESS_CHANNEL_PREFIX = "job_progress:"


# ---------------------------------------------------------------------------
# Sync Redis helper (Celery tasks run in sync context)
# ---------------------------------------------------------------------------

def _get_sync_redis():
    import redis as sync_redis
    return sync_redis.from_url(settings.REDIS_URL, decode_responses=True)


def _publish_progress(
    redis_client,
    job_id: str,
    status: str,
    stage: str,
    progress: int,
    message: str,
    error: str | None = None,
) -> None:
    payload = {
        "job_id": job_id,
        "status": status,
        "stage": stage,
        "progress": progress,
        "message": message,
        "error": error,
    }
    channel = f"{PROGRESS_CHANNEL_PREFIX}{job_id}"
    redis_client.publish(channel, json.dumps(payload))
    logger.debug(
    f"progress_published | channel={channel} | progress={progress}"
)


# ---------------------------------------------------------------------------
# DB helpers (sync — run inside sync Celery task)
# ---------------------------------------------------------------------------

def _sync_update_job(
    job_id: str,
    status: str,
    progress: int,
    pipeline_stage: str | None = None,
    error_message: str | None = None,
    audio_metadata: dict | None = None,
    duration_seconds: float | None = None,
) -> None:
    """Synchronously update the job row using a new SQLAlchemy sync engine."""
    from sqlalchemy import create_engine, update
    from sqlalchemy.orm import Session
    from app.models.job import Job, JobStatus

    # Build a sync version of the DATABASE_URL (replace asyncpg with psycopg2)
    sync_url = settings.DATABASE_URL.replace("+asyncpg", "+psycopg2")

    engine = create_engine(sync_url, pool_pre_ping=True, pool_size=2, max_overflow=4)
    values: dict[str, Any] = {"status": JobStatus(status), "progress": progress}

    if pipeline_stage is not None:
        values["pipeline_stage"] = pipeline_stage
    if error_message is not None:
        values["error_message"] = error_message
    if audio_metadata is not None:
        values["audio_metadata"] = audio_metadata
    if duration_seconds is not None:
        values["duration_seconds"] = duration_seconds

    with Session(engine) as session:
        session.execute(update(Job).where(Job.id == uuid.UUID(job_id)).values(**values))
        session.commit()

    engine.dispose()


# ---------------------------------------------------------------------------
# Celery Task
# ---------------------------------------------------------------------------

class AudioProcessingTask(Task):
    """Base class with shared error handling."""

    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        job_id = kwargs.get("job_id") or (args[0] if args else None)
        if job_id:
            try:
                _sync_update_job(
                    job_id=job_id,
                    status="FAILED",
                    progress=0,
                    error_message=str(exc)[:1024],
                )
                redis = _get_sync_redis()
                _publish_progress(
                    redis,
                    job_id=job_id,
                    status="FAILED",
                    stage="",
                    progress=0,
                    message="Processing failed",
                    error=str(exc)[:512],
                )
                redis.close()
            except Exception as publish_exc:
                logger.error(
                    f"on_failure_publish_error | error={publish_exc}")
        super().on_failure(exc, task_id, args, kwargs, einfo)


@celery_app.task(
    bind=True,
    base=AudioProcessingTask,
    name="app.workers.tasks.process_audio.process_audio_task",
    queue="audio_processing",
    max_retries=3,
    default_retry_delay=15,
    soft_time_limit=600,   # 10 min — warn
    time_limit=660,        # 11 min — hard kill
)
def process_audio_task(self: Task, job_id: str, s3_key: str) -> dict:
    """
    Phase 3 processing pipeline for a single audio upload.

    Steps:
        1. Download file from MinIO to a temp file
        2. Extract audio metadata (duration, sample rate, channels, bitrate)
        3. Update job record with metadata
        4. Mark job COMPLETED

    Args:
        job_id: UUID string of the Job record.
        s3_key:  MinIO storage key of the uploaded audio file.

    Returns:
        dict with extracted metadata summary.
    """
    redis = _get_sync_redis()

    def progress(status: str, stage: str, pct: int, msg: str) -> None:
        _sync_update_job(job_id=job_id, status=status, progress=pct, pipeline_stage=stage)
        _publish_progress(redis, job_id, status, stage, pct, msg)
        logger.info(
            f"task_progress | job_id={job_id} | stage={stage} | progress={pct}%"
            )

    try:
        logger.info(
            f"process_audio_start | job_id={job_id} | s3_key={s3_key}"
            )

        # ── Step 1: Download from MinIO ────────────────────────────────────
        progress("PREPROCESSING", "DOWNLOADING", 10, "Downloading audio file…")

        from minio import Minio
        minio_client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )

        # Infer extension from s3_key
        ext = os.path.splitext(s3_key)[-1] or ".audio"

        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp_path = tmp.name

        try:
            minio_client.fget_object(settings.MINIO_BUCKET, s3_key, tmp_path)
            logger.info(
                f"file_downloaded | job_id={job_id} | tmp_path={tmp_path}"
                )
            
            progress("PREPROCESSING", "PREPROCESSING", 20, "Preparing audio...")

            preprocessor = PreprocessingService()

            audio_input = AudioInput(
                file_path=Path(tmp_path),
                original_filename=os.path.basename(tmp_path),
                job_id=job_id,
            )

            context = StageContext(
                job_id=job_id,
                stage="preprocessing",
            )

            result = asyncio.run(
                preprocessor.process(
                    input=audio_input,
                    context=context,
                )
            )

            logger.info(
                f"preprocessing_complete | job_id={job_id}"
            )

            # ── Step 3: Persist metadata to DB ─────────────────────────────
            _sync_update_job(
                job_id=job_id,
                status="PREPROCESSING",
                progress=80,
                pipeline_stage="SAVING_METADATA",
                audio_metadata=meta_dict,
                duration_seconds=metadata.duration_seconds,
            )
            # ── Step 4: Mark COMPLETED ─────────────────────────────────────
            _sync_update_job(
                job_id=job_id,
                status="COMPLETED",
                progress=100,
                pipeline_stage=None,
            )
            _publish_progress(
                redis,
                job_id=job_id,
                status="COMPLETED",
                stage="COMPLETED",
                progress=100,
                message="Processing complete",
            )

            logger.info(
                f"process_audio_complete | job_id={job_id} | duration={metadata.duration_seconds}s | format={metadata.format}"
                )
            return meta_dict

        finally:
            # Always clean up the temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                logger.debug(
                    f"tmp_file_deleted | path={tmp_path}"
                    )

    except Exception as exc:
        logger.exception(
            f"process_audio_error | job_id={job_id} | error={exc}"
            )
        # Retry on transient errors (network/DB)
        raise self.retry(exc=exc)
    finally:
        try:
            redis.close()
        except Exception:
            pass
