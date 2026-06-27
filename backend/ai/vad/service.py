"""
VADService — clean service interface for Voice Activity Detection.

Wraps the concrete SileroVAD implementation behind a stable interface.
Business logic stays here; FastAPI routes never touch SileroVAD directly.
"""

from __future__ import annotations

import time

from ai.interfaces.base_stage import BaseStage, StageContext
from ai.preprocessing.models import AudioSegment
from .silero_vad import SileroVAD
from .models import VADResult


class VADService(BaseStage[AudioSegment, VADResult]):
    """Voice Activity Detection service — strips silence before diarization."""

    stage_name = "vad"

    def __init__(self, threshold: float = 0.5) -> None:
        super().__init__()
        self._vad = SileroVAD(threshold=threshold)

    async def load(self) -> None:
        await self._vad.load()
        self._loaded = True

    async def unload(self) -> None:
        await self._vad.unload()
        self._loaded = False

    async def process(
        self, input: AudioSegment, context: StageContext
    ) -> VADResult:
        self._log_start(context)
        t0 = time.perf_counter()
        try:
            result = await self._vad.detect(input, context.job_id)
            duration = time.perf_counter() - t0
            self._log_success(
                context,
                duration,
                {
                    "speech_segments": len(result.activity.speech_segments),
                    "speech_ratio": result.activity.speech_ratio,
                    "total_speech_seconds": result.activity.total_speech_seconds,
                },
            )
            return result
        except Exception as exc:
            self._log_failure(context, time.perf_counter() - t0, exc)
            raise
