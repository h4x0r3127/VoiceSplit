"""
BaseStage — the universal contract for every AI pipeline stage.

Design principles (SOLID):
  - Single Responsibility : each stage does exactly one transformation.
  - Open/Closed           : new stages extend BaseStage; existing stages unchanged.
  - Liskov Substitution   : any concrete stage is substitutable.
  - Interface Segregation : ILoadable / IProcessable are separate protocols.
  - Dependency Inversion  : PipelineManager depends on BaseStage, not implementations.

Every stage implementation MUST:
  1. Declare ``stage_name`` as a class-level constant.
  2. Implement ``process()`` accepting strongly-typed Pydantic input/output.
  3. Optionally implement ``load()`` / ``unload()`` for heavy model management.

Structured logging is injected automatically; each stage should call
``self._log_start()``, ``self._log_success()``, and ``self._log_failure()``
to emit consistent JSON log lines.
"""

from __future__ import annotations

import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, ClassVar, Generic, Optional, TypeVar

from pydantic import BaseModel

from app.core.logging_config import get_stage_logger

InputT = TypeVar("InputT", bound=BaseModel)
OutputT = TypeVar("OutputT", bound=BaseModel)


# ─────────────────────────────────────────────────────────────────────────────
# Context object — threaded through the full pipeline call
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class StageContext:
    """Immutable context passed to every stage during pipeline execution.

    Attributes
    ----------
    job_id:
        Unique identifier for the parent processing job (UUID string).
    trace_id:
        Correlation ID for distributed tracing (defaults to a new UUID).
    extra:
        Arbitrary extra data attached by the pipeline orchestrator.
    """

    job_id: str
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    extra: dict[str, Any] = field(default_factory=dict)


# ─────────────────────────────────────────────────────────────────────────────
# Metadata model — returned alongside stage output for observability
# ─────────────────────────────────────────────────────────────────────────────

class StageMeta(BaseModel):
    """Execution metadata emitted by every stage run."""

    stage_name: str
    job_id: str
    trace_id: str
    duration_seconds: float
    success: bool
    warnings: list[str] = []
    errors: list[str] = []
    output_stats: dict[str, Any] = {}


# ─────────────────────────────────────────────────────────────────────────────
# BaseStage — abstract generic base
# ─────────────────────────────────────────────────────────────────────────────

class BaseStage(ABC, Generic[InputT, OutputT]):
    """Abstract base class for all VoiceSplit AI pipeline stages.

    Subclass example
    ----------------
    ::

        class MyStage(BaseStage[MyInput, MyOutput]):
            stage_name: ClassVar[str] = "my_stage"

            async def process(
                self, input: MyInput, context: StageContext
            ) -> MyOutput:
                self._log_start(context)
                t0 = time.perf_counter()
                try:
                    result = await self._run(input)
                    self._log_success(context, time.perf_counter() - t0, {...})
                    return result
                except Exception as exc:
                    self._log_failure(context, time.perf_counter() - t0, exc)
                    raise
    """

    stage_name: ClassVar[str] = "unnamed_stage"

    def __init__(self) -> None:
        self._logger = get_stage_logger(self.stage_name)
        self._loaded: bool = False
        self._warnings: list[str] = []

    # ── Lifecycle ──────────────────────────────────────────────────────────────

    async def load(self) -> None:
        """Load model weights / expensive resources. Override when needed."""
        self._loaded = True

    async def unload(self) -> None:
        """Release resources held by this stage. Override when needed."""
        self._loaded = False

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    # ── Core contract ──────────────────────────────────────────────────────────

    @abstractmethod
    async def process(self, input: InputT, context: StageContext) -> OutputT:
        """Execute this stage's transformation.

        Parameters
        ----------
        input:
            Strongly-typed Pydantic model produced by the preceding stage (or
            the pipeline's initial input).
        context:
            Pipeline context providing job_id, trace_id, and extra metadata.

        Returns
        -------
        OutputT
            Strongly-typed Pydantic model to be forwarded to the next stage.
        """

    # ── Structured logging helpers ─────────────────────────────────────────────

    def _log_start(self, context: StageContext) -> None:
        self._warnings = []
        self._logger.info(
            "stage_start",
            stage=self.stage_name,
            job_id=context.job_id,
            trace_id=context.trace_id,
        )

    def _log_success(
        self,
        context: StageContext,
        duration: float,
        output_stats: Optional[dict[str, Any]] = None,
    ) -> None:
        self._logger.info(
            "stage_success",
            stage=self.stage_name,
            job_id=context.job_id,
            trace_id=context.trace_id,
            duration_seconds=round(duration, 4),
            warnings=self._warnings,
            output_stats=output_stats or {},
        )

    def _log_failure(
        self,
        context: StageContext,
        duration: float,
        exc: Exception,
    ) -> None:
        self._logger.error(
            "stage_failure",
            stage=self.stage_name,
            job_id=context.job_id,
            trace_id=context.trace_id,
            duration_seconds=round(duration, 4),
            error=str(exc),
            error_type=type(exc).__name__,
            warnings=self._warnings,
        )

    def _warn(self, message: str, context: Optional[StageContext] = None) -> None:
        self._warnings.append(message)
        self._logger.warning(
            "stage_warning",
            stage=self.stage_name,
            job_id=context.job_id if context else "unknown",
            message=message,
        )

    def build_meta(
        self,
        context: StageContext,
        duration: float,
        success: bool,
        output_stats: Optional[dict[str, Any]] = None,
        errors: Optional[list[str]] = None,
    ) -> StageMeta:
        """Construct a StageMeta from the current execution state."""
        return StageMeta(
            stage_name=self.stage_name,
            job_id=context.job_id,
            trace_id=context.trace_id,
            duration_seconds=round(duration, 4),
            success=success,
            warnings=list(self._warnings),
            errors=errors or [],
            output_stats=output_stats or {},
        )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} stage={self.stage_name!r} loaded={self._loaded}>"
