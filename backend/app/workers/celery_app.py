"""Celery application factory for VoiceSplit background workers.

Broker:  Redis (REDIS_URL env var)
Backend: Redis (same URL)

The Celery app is importable by both the FastAPI app (for task dispatch)
and the worker process (for task discovery).
"""
from __future__ import annotations

from celery import Celery
from celery.utils.log import get_task_logger

from app.config import settings

celery_app = Celery(
    "voicesplit",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.tasks.process_audio"],
)

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    # Timezone
    timezone="UTC",
    enable_utc=True,
    # Task behaviour
    task_acks_late=True,          # Ack only after task completes (safe retry on crash)
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1, # One task per worker at a time (audio tasks are heavy)
    # Result retention (24 hours)
    result_expires=86400,
    # Retry policy defaults
    task_max_retries=3,
    task_default_retry_delay=10,  # seconds
    # Routing
    task_routes={
        "app.workers.tasks.process_audio.process_audio_task": {
            "queue": "audio_processing"
        },
    },
    # Beat schedule (empty for Phase 3 — will add cleanup job in Phase 5)
    beat_schedule={},
)

logger = get_task_logger(__name__)
