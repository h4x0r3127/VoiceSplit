"""
AI pipeline utilities — shared helpers for all pipeline stages.

Includes:
- Execution timer context manager
- Audio segment slicing helpers
- Color palette assignment for speaker tracks
- Stage-level logging helpers
"""
from __future__ import annotations

import time
import uuid
import contextlib
from typing import Any, Generator, Optional

from app.utils.logging import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Brand colour palette — assigned to speakers in order, cycling if > 8
# ---------------------------------------------------------------------------

SPEAKER_COLORS: list[str] = [
    "#06D6CF",  # brand cyan
    "#3B82F6",  # brand blue
    "#7C3AED",  # brand purple
    "#F59E0B",  # amber
    "#EC4899",  # pink
    "#10B981",  # emerald
    "#F97316",  # orange
    "#6366F1",  # indigo
]


def get_speaker_color(index: int) -> str:
    """Return a brand color for speaker at *index* (cycles if > len)."""
    return SPEAKER_COLORS[index % len(SPEAKER_COLORS)]


def generate_speaker_label(index: int) -> str:
    """Return human-readable label, e.g. 'Speaker 1'."""
    return f"Speaker {index + 1}"


def generate_speaker_id() -> str:
    """Return a new unique speaker UUID string."""
    return f"spk_{uuid.uuid4().hex[:8]}"


# ---------------------------------------------------------------------------
# Execution timer
# ---------------------------------------------------------------------------

@contextlib.contextmanager
def stage_timer(stage_name: str, job_id: Optional[str] = None) -> Generator[dict[str, Any], None, None]:
    """
    Context manager that times a pipeline stage and logs the result.

    Usage::

        with stage_timer("VAD", job_id=job_id) as t:
            result = do_work()
        # t["duration_ms"] is now populated

    Yields a mutable dict with keys:
        start_ms, end_ms, duration_ms (populated on __exit__)
    """
    ctx: dict[str, Any] = {"start_ms": time.monotonic() * 1000}
    log_ctx = {"stage": stage_name}
    if job_id:
        log_ctx["job_id"] = job_id

    logger.info("stage_start", **log_ctx)
    try:
        yield ctx
        ctx["end_ms"] = time.monotonic() * 1000
        ctx["duration_ms"] = ctx["end_ms"] - ctx["start_ms"]
        logger.info(
            "stage_complete",
            duration_ms=round(ctx["duration_ms"], 2),
            **log_ctx,
        )
    except Exception as exc:
        ctx["end_ms"] = time.monotonic() * 1000
        ctx["duration_ms"] = ctx["end_ms"] - ctx["start_ms"]
        logger.error(
            "stage_failed",
            error=str(exc),
            duration_ms=round(ctx["duration_ms"], 2),
            **log_ctx,
        )
        raise


# ---------------------------------------------------------------------------
# Audio segment helpers (numpy-free — indices only)
# ---------------------------------------------------------------------------

def segment_sample_range(
    start_sec: float,
    end_sec: float,
    sample_rate: int,
) -> tuple[int, int]:
    """Convert time range (seconds) to sample indices."""
    return int(start_sec * sample_rate), int(end_sec * sample_rate)


def clamp_segment(
    start: float,
    end: float,
    max_duration: float,
) -> tuple[float, float]:
    """Clamp a segment to within [0, max_duration]."""
    return max(0.0, start), min(max_duration, end)


# ---------------------------------------------------------------------------
# Result validation helpers
# ---------------------------------------------------------------------------

def validate_segments_coverage(
    segments: list[Any],
    total_duration: float,
    stage: str,
) -> None:
    """
    Log a warning if detected speech segments seem implausible.

    Args:
        segments: List of objects with .start and .end float attributes.
        total_duration: Total audio duration in seconds.
        stage: Stage name for log context.
    """
    if not segments:
        logger.warning("no_segments_detected", stage=stage, duration=total_duration)
        return

    covered = sum(getattr(s, "end", 0) - getattr(s, "start", 0) for s in segments)
    ratio = covered / max(total_duration, 0.001)

    if ratio < 0.05:
        logger.warning(
            "very_low_speech_ratio",
            stage=stage,
            speech_ratio=round(ratio, 3),
            covered_s=round(covered, 2),
            total_s=round(total_duration, 2),
        )
    elif ratio > 1.0:
        logger.warning(
            "speech_ratio_exceeds_total",
            stage=stage,
            speech_ratio=round(ratio, 3),
        )
    else:
        logger.debug(
            "segment_coverage_ok",
            stage=stage,
            speech_ratio=round(ratio, 3),
        )
