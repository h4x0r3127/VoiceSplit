"""
PreprocessingService — clean service interface for the preprocessing stage.

Responsibilities (Single Responsibility Principle):
  - Accept a raw uploaded file path
  - Delegate to AudioLoader, AudioResampler, AudioNormalizer
  - Return a strongly-typed PreprocessingResult

FastAPI routes and Celery tasks MUST NOT call AudioLoader / Resampler directly.
They interact only through PreprocessingService.
"""

from __future__ import annotations

import time

from ai.interfaces.base_stage import BaseStage, StageContext
from .audio_loader import AudioLoader
from .normalizer import AudioNormalizer
from .resampler import AudioResampler
from .models import AudioInput, PreprocessingResult


class PreprocessingService(BaseStage[AudioInput, PreprocessingResult]):
    """Orchestrates all audio pre-processing sub-steps for one job."""

    stage_name = "preprocessing"

    def __init__(self) -> None:
        super().__init__()
        self._loader = AudioLoader()
        self._resampler = AudioResampler()
        self._normalizer = AudioNormalizer()

    async def process(
        self, input: AudioInput, context: StageContext
    ) -> PreprocessingResult:
        self._log_start(context)
        t0 = time.perf_counter()
        try:
            # 1. Load & decode
            raw_segment = await self._loader.load(input)

            # 2. Resample to target rate / channels
            resampled, was_converted, orig_sr, orig_ch = (
                await self._resampler.resample(raw_segment, input)
            )

            # 3. Normalise amplitude
            normalised = await self._normalizer.normalise(resampled)

            duration = time.perf_counter() - t0
            result = PreprocessingResult(
                job_id=input.job_id,
                segment=normalised,
                was_converted=was_converted,
                original_sample_rate=orig_sr,
                original_channels=orig_ch,
            )
            self._log_success(
                context,
                duration,
                {
                    "sample_rate": normalised.sample_rate,
                    "duration_seconds": normalised.duration_seconds,
                    "channels": normalised.channels,
                    "was_converted": was_converted,
                },
            )
            return result
        except Exception as exc:
            self._log_failure(context, time.perf_counter() - t0, exc)
            raise
