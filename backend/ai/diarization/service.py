"""
DiarizationService — clean service interface for speaker diarization.

Wraps PyannoteDriver behind a stable BaseStage interface.
Routes / workers only call DiarizationService; they never import pyannote.
"""

from __future__ import annotations

import time

from ai.interfaces.base_stage import BaseStage, StageContext
from ai.preprocessing.models import AudioSegment
from .pyannote_diarizer import PyannoteDriver
from .models import DiarizationResult


class DiarizationService(BaseStage[AudioSegment, DiarizationResult]):
    """Speaker diarization — assigns time segments to distinct speakers."""

    stage_name = "diarization"

    def __init__(
        self,
        hf_token: str,
        min_speakers: int = 1,
        max_speakers: int = 8,
    ) -> None:
        super().__init__()
        self._driver = PyannoteDriver(
            hf_token=hf_token,
            min_speakers=min_speakers,
            max_speakers=max_speakers,
        )

    async def load(self) -> None:
        await self._driver.load()
        self._loaded = True

    async def unload(self) -> None:
        await self._driver.unload()
        self._loaded = False

    async def process(
        self, input: AudioSegment, context: StageContext
    ) -> DiarizationResult:
        self._log_start(context)
        t0 = time.perf_counter()
        try:
            result = await self._driver.diarize(input, context.job_id)
            duration = time.perf_counter() - t0
            self._log_success(
                context,
                duration,
                {
                    "num_speakers": result.num_speakers,
                    "num_segments": len(result.segments),
                },
            )
            return result
        except Exception as exc:
            self._log_failure(context, time.perf_counter() - t0, exc)
            raise
