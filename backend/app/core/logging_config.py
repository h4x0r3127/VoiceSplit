"""
Structured logging configuration for VoiceSplit.

Provides two logging modes controlled by the ENVIRONMENT setting:
  - development : human-readable coloured output via ``logging.StreamHandler``
  - production  : JSON-formatted output (one JSON object per line) suitable
                  for ingestion by Elasticsearch, Loki, Datadog, etc.

Usage
-----
    from app.core.logging_config import get_stage_logger, setup_logging

    # Call once at application startup (e.g. in main.py lifespan):
    setup_logging()

    # Obtain a named logger for an AI stage:
    logger = get_stage_logger("preprocessing")
    logger.info("stage_start", stage="preprocessing", job_id="abc-123")
"""

from __future__ import annotations

import json
import logging
import sys
import time
from typing import Any

# ─────────────────────────────────────────────────────────────────────────────
# JSON Formatter
# ─────────────────────────────────────────────────────────────────────────────

class _JsonFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects.

    Each log line has the schema::

        {
          "timestamp": "<ISO-8601>",
          "level":     "INFO",
          "logger":    "ai.preprocessing",
          "event":     "stage_success",
          "duration_seconds": 1.23,
          ...           (any extra kwargs passed to logger.info(...))
        }
    """

    def format(self, record: logging.LogRecord) -> str:  # noqa: D102
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S.%f"),
            "level": record.levelname,
            "logger": record.name,
            "event": record.getMessage(),
        }
        # Merge any extra keyword arguments attached to the record
        for key, value in record.__dict__.items():
            if key not in {
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "exc_info", "exc_text", "stack_info",
                "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "message",
                "taskName",
            }:
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


# ─────────────────────────────────────────────────────────────────────────────
# Human-readable development formatter
# ─────────────────────────────────────────────────────────────────────────────

_DEV_FORMAT = (
    "%(asctime)s │ %(levelname)-8s │ %(name)-30s │ %(message)s"
)


# ─────────────────────────────────────────────────────────────────────────────
# Stage-aware logger adapter
# ─────────────────────────────────────────────────────────────────────────────

class _StageLogger:
    """Thin wrapper around ``logging.Logger`` that injects structured kwargs.

    Instead of ``logger.info("msg %s", arg)``, callers use keyword syntax::

        logger.info("stage_success", duration_seconds=0.42, job_id="xyz")

    This maps cleanly to the JSON formatter's extra-field merging.
    """

    def __init__(self, inner: logging.Logger) -> None:
        self._inner = inner

    def _emit(self, level: int, event: str, **kwargs: Any) -> None:
        if self._inner.isEnabledFor(level):
            self._inner.log(
            level,
            event,
            extra=kwargs,
            stacklevel=3,
        )

    def debug(self, event: str, **kwargs: Any) -> None:
        self._emit(logging.DEBUG, event, **kwargs)

    def info(self, event: str, **kwargs: Any) -> None:
        self._emit(logging.INFO, event, **kwargs)

    def warning(self, event: str, **kwargs: Any) -> None:
        self._emit(logging.WARNING, event, **kwargs)

    def error(self, event: str, **kwargs: Any) -> None:
        self._emit(logging.ERROR, event, **kwargs)

    def critical(self, event: str, **kwargs: Any) -> None:
        self._emit(logging.CRITICAL, event, **kwargs)


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

_configured: bool = False


def setup_logging(environment: str = "development", log_level: str = "INFO") -> None:
    """Configure the root logger.  Call once at application startup.

    Parameters
    ----------
    environment:
        ``"production"`` enables JSON output; anything else enables the
        coloured development format.
    log_level:
        Standard Python log-level string (``"DEBUG"``, ``"INFO"``, etc.).
    """
    global _configured
    if _configured:
        return

    level = getattr(logging, log_level.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    if environment == "production":
        handler.setFormatter(_JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter(_DEV_FORMAT, datefmt="%H:%M:%S"))

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    # Suppress noisy third-party loggers in production
    for noisy in ("uvicorn.access", "httpx", "httpcore"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    _configured = True


def get_stage_logger(stage_name: str) -> _StageLogger:
    """Return a structured logger scoped to an AI stage.

    Parameters
    ----------
    stage_name:
        Short identifier for the stage (e.g. ``"preprocessing"``).
        The underlying logger name will be ``ai.<stage_name>``.
    """
    inner = logging.getLogger(f"ai.{stage_name}")
    return _StageLogger(inner)


def get_logger(name: str) -> _StageLogger:
    """Return a structured logger for any component (not just AI stages)."""
    inner = logging.getLogger(name)
    return _StageLogger(inner)
