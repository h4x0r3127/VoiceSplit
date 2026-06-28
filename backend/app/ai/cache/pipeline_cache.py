"""
Pipeline result cache — stores intermediate and final AI results in Redis.

Purpose:
    - Avoid re-processing if a job is retried due to a transient error
    - Cache stage outputs so individual stages can be re-run independently
    - Store speaker previews and embedding vectors between pipeline runs

Cache keys follow the pattern:
    pipeline:{job_id}:stage:{stage_name}         -> JSON result
    pipeline:{job_id}:speakers                   -> JSON speaker profiles
    pipeline:{job_id}:transcript                 -> JSON transcript
    pipeline:{job_id}:status                     -> JSON processing status

All entries have a configurable TTL (default 24 hours).
"""
from __future__ import annotations

import json
from typing import Any, Optional

from app.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)

_DEFAULT_TTL_SECONDS = 86_400  # 24 hours

_KEY_STAGE     = "pipeline:{job_id}:stage:{stage}"
_KEY_SPEAKERS  = "pipeline:{job_id}:speakers"
_KEY_TRANSCRIPT = "pipeline:{job_id}:transcript"
_KEY_STATUS    = "pipeline:{job_id}:status"
_KEY_FULL      = "pipeline:{job_id}:result"


class PipelineCache:
    """
    Redis-backed cache for AI pipeline stage results.

    Dependency-injected into PipelineManager — does not create its own
    Redis connection, accepts one from the caller for lifecycle management.

    Usage::

        cache = PipelineCache(redis_client)
        await cache.set_stage_result(job_id, "VAD", vad_result.model_dump())
        cached = await cache.get_stage_result(job_id, "VAD")
    """

    def __init__(self, redis_client: Any, ttl_seconds: int = _DEFAULT_TTL_SECONDS) -> None:
        self._redis = redis_client
        self._ttl = ttl_seconds

    # ------------------------------------------------------------------
    # Stage results
    # ------------------------------------------------------------------

    async def set_stage_result(
        self,
        job_id: str,
        stage: str,
        data: dict[str, Any],
    ) -> None:
        key = _KEY_STAGE.format(job_id=job_id, stage=stage)
        try:
            await self._redis.setex(key, self._ttl, json.dumps(data))
            logger.debug("cache_set_stage", job_id=job_id, stage=stage, key=key)
        except Exception as exc:
            logger.warning("cache_set_stage_failed", job_id=job_id, stage=stage, error=str(exc))

    async def get_stage_result(
        self,
        job_id: str,
        stage: str,
    ) -> Optional[dict[str, Any]]:
        key = _KEY_STAGE.format(job_id=job_id, stage=stage)
        try:
            raw = await self._redis.get(key)
            if raw is None:
                return None
            logger.debug("cache_hit_stage", job_id=job_id, stage=stage)
            return json.loads(raw)
        except Exception as exc:
            logger.warning("cache_get_stage_failed", job_id=job_id, stage=stage, error=str(exc))
            return None

    async def has_stage_result(self, job_id: str, stage: str) -> bool:
        key = _KEY_STAGE.format(job_id=job_id, stage=stage)
        try:
            return bool(await self._redis.exists(key))
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Processing status
    # ------------------------------------------------------------------

    async def set_status(self, job_id: str, status: dict[str, Any]) -> None:
        key = _KEY_STATUS.format(job_id=job_id)
        try:
            await self._redis.setex(key, self._ttl, json.dumps(status))
        except Exception as exc:
            logger.warning("cache_set_status_failed", job_id=job_id, error=str(exc))

    async def get_status(self, job_id: str) -> Optional[dict[str, Any]]:
        key = _KEY_STATUS.format(job_id=job_id)
        try:
            raw = await self._redis.get(key)
            return json.loads(raw) if raw else None
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Speaker profiles
    # ------------------------------------------------------------------

    async def set_speakers(self, job_id: str, speakers: list[dict[str, Any]]) -> None:
        key = _KEY_SPEAKERS.format(job_id=job_id)
        try:
            await self._redis.setex(key, self._ttl, json.dumps(speakers))
            logger.debug("cache_set_speakers", job_id=job_id, count=len(speakers))
        except Exception as exc:
            logger.warning("cache_set_speakers_failed", job_id=job_id, error=str(exc))

    async def get_speakers(self, job_id: str) -> Optional[list[dict[str, Any]]]:
        key = _KEY_SPEAKERS.format(job_id=job_id)
        try:
            raw = await self._redis.get(key)
            return json.loads(raw) if raw else None
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Transcript
    # ------------------------------------------------------------------

    async def set_transcript(self, job_id: str, transcript: dict[str, Any]) -> None:
        key = _KEY_TRANSCRIPT.format(job_id=job_id)
        try:
            await self._redis.setex(key, self._ttl, json.dumps(transcript))
        except Exception as exc:
            logger.warning("cache_set_transcript_failed", job_id=job_id, error=str(exc))

    async def get_transcript(self, job_id: str) -> Optional[dict[str, Any]]:
        key = _KEY_TRANSCRIPT.format(job_id=job_id)
        try:
            raw = await self._redis.get(key)
            return json.loads(raw) if raw else None
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Full pipeline result
    # ------------------------------------------------------------------

    async def set_pipeline_result(self, job_id: str, result: dict[str, Any]) -> None:
        key = _KEY_FULL.format(job_id=job_id)
        try:
            await self._redis.setex(key, self._ttl, json.dumps(result))
            logger.info("cache_set_pipeline_result", job_id=job_id)
        except Exception as exc:
            logger.warning("cache_set_pipeline_result_failed", job_id=job_id, error=str(exc))

    async def get_pipeline_result(self, job_id: str) -> Optional[dict[str, Any]]:
        key = _KEY_FULL.format(job_id=job_id)
        try:
            raw = await self._redis.get(key)
            return json.loads(raw) if raw else None
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Invalidation
    # ------------------------------------------------------------------

    async def invalidate_job(self, job_id: str) -> None:
        """Delete all cache keys for a job (e.g. on re-process request)."""
        pattern = f"pipeline:{job_id}:*"
        try:
            keys = await self._redis.keys(pattern)
            if keys:
                await self._redis.delete(*keys)
                logger.info("cache_invalidated_job", job_id=job_id, keys_deleted=len(keys))
        except Exception as exc:
            logger.warning("cache_invalidate_failed", job_id=job_id, error=str(exc))
