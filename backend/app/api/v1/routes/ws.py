"""
WebSocket endpoint for real-time job progress streaming.

Connection: GET /api/v1/ws/jobs/{job_id}?token=<jwt>

Protocol:
  - Client connects with a valid JWT in the query string
  - Server verifies ownership of the job
  - Server subscribes to Redis pub/sub channel  job_progress:<job_id>
  - Each published message is forwarded as a JSON text frame
  - Server sends a heartbeat ping every 25 seconds
  - Connection closes when job reaches COMPLETED or FAILED status

Message schema (JSON):
  {
    "job_id":  "uuid",
    "status":  "PREPROCESSING" | "COMPLETED" | "FAILED" | ...,
    "stage":   "DOWNLOADING" | "EXTRACTING_METADATA" | ...,
    "progress": 0-100,
    "message": "human readable",
    "error":   null | "string"
  }
"""
from __future__ import annotations

import asyncio
import json
import uuid
from typing import AsyncGenerator

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from starlette.websockets import WebSocketState

from app.config import settings
from app.core.auth import decode_token
from app.database import AsyncSessionLocal
from app.models.job import JobStatus
from app.repositories.job_repo import JobRepository
from app.utils.logging import get_logger

router = APIRouter(prefix="/ws", tags=["websocket"])
logger = get_logger(__name__)

_job_repo = JobRepository()

HEARTBEAT_INTERVAL = 25  # seconds
TERMINAL_STATUSES = {JobStatus.COMPLETED, JobStatus.FAILED}


@router.websocket("/jobs/{job_id}")
async def job_progress_ws(websocket: WebSocket, job_id: uuid.UUID) -> None:
    """
    Stream real-time job processing progress to the client via WebSocket.
    Authenticates using `?token=<jwt>` query parameter.
    """
    token = websocket.query_params.get("token")

    # ── Auth ──────────────────────────────────────────────────────────────
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        payload = decode_token(token)
        user_id = uuid.UUID(payload["sub"])
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # ── Accept connection ────────────────────────────────────────────────
    await websocket.accept()
    logger.info("ws_connected", job_id=str(job_id), user_id=str(user_id))

    # ── Verify job ownership ─────────────────────────────────────────────
    async with AsyncSessionLocal() as db:
        job = await _job_repo.get_by_id(db, job_id)

    if not job or job.user_id != user_id:
        await websocket.send_json({"error": "Job not found or access denied"})
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # If job is already terminal, send final state and close
    if job.status in TERMINAL_STATUSES:
        await websocket.send_json({
            "job_id": str(job_id),
            "status": job.status.value,
            "stage": job.pipeline_stage or job.status.value,
            "progress": job.progress,
            "message": "Processing complete" if job.status == JobStatus.COMPLETED else job.error_message,
            "error": job.error_message,
        })
        await websocket.close()
        return

    # ── Subscribe to Redis pub/sub ─────────────────────────────────────
    import redis.asyncio as aioredis
    channel = f"job_progress:{job_id}"

    async_redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    pubsub = async_redis.pubsub()
    await pubsub.subscribe(channel)

    try:
        heartbeat_task = asyncio.create_task(
            _heartbeat_loop(websocket, HEARTBEAT_INTERVAL)
        )

        async for message in _iter_pubsub(pubsub, timeout=300.0):
            if websocket.client_state != WebSocketState.CONNECTED:
                break

            if message is None:
                # Timeout — re-check job status from DB
                async with AsyncSessionLocal() as db:
                    job = await _job_repo.get_by_id(db, job_id)
                if job and job.status in TERMINAL_STATUSES:
                    await websocket.send_json({
                        "job_id": str(job_id),
                        "status": job.status.value,
                        "stage": job.status.value,
                        "progress": job.progress,
                        "message": "Processing complete",
                        "error": job.error_message,
                    })
                    break
                continue

            try:
                await websocket.send_text(message)
                data = json.loads(message)
                if data.get("status") in ("COMPLETED", "FAILED"):
                    break
            except Exception as send_exc:
                logger.warning("ws_send_error", error=str(send_exc))
                break

    except WebSocketDisconnect:
        logger.info("ws_client_disconnected", job_id=str(job_id))
    except Exception as exc:
        logger.error("ws_error", job_id=str(job_id), error=str(exc))
    finally:
        heartbeat_task.cancel()
        await pubsub.unsubscribe(channel)
        await pubsub.aclose()
        await async_redis.aclose()
        logger.info("ws_closed", job_id=str(job_id))


async def _heartbeat_loop(websocket: WebSocket, interval: int) -> None:
    """Send periodic ping frames to keep the connection alive."""
    try:
        while websocket.client_state == WebSocketState.CONNECTED:
            await asyncio.sleep(interval)
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_json({"type": "ping"})
    except (WebSocketDisconnect, RuntimeError, asyncio.CancelledError):
        pass


async def _iter_pubsub(
    pubsub, timeout: float = 300.0
) -> AsyncGenerator[str | None, None]:
    """
    Async generator that yields raw message strings from a Redis pub/sub subscription.
    Yields None on timeout so the caller can poll DB for terminal state.
    """
    deadline = asyncio.get_event_loop().time() + timeout
    while asyncio.get_event_loop().time() < deadline:
        msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=5.0)
        if msg and msg["type"] == "message":
            yield msg["data"]
        else:
            yield None
