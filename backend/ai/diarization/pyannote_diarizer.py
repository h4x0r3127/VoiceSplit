"""
PyannoteDriver — concrete driver for pyannote.audio speaker diarization.

Model: pyannote/speaker-diarization-3.1
  https://huggingface.co/pyannote/speaker-diarization-3.1
Requires accepting the HuggingFace model terms and a valid HF_TOKEN.

This driver is isolated from DiarizationService so the backend model
can be swapped (e.g. NeMo MSDD) without touching the service interface.
"""

from __future__ import annotations

from ai.interfaces.protocols import ILoadable
from ai.preprocessing.models import AudioSegment
from .models import DiarizationResult, DiarizationSegment, Speaker


class PyannoteDriver(ILoadable):
    """Wraps pyannote.audio Pipeline for speaker diarization."""

    PIPELINE_ID = "pyannote/speaker-diarization-3.1"

    def __init__(
        self,
        hf_token: str,
        min_speakers: int = 1,
        max_speakers: int = 8,
    ) -> None:
        self._hf_token = hf_token
        self._min_speakers = min_speakers
        self._max_speakers = max_speakers
        self._pipeline = None
        self._loaded_flag = False

    async def load(self) -> None:
        """Download and instantiate the pyannote pipeline (cached on disk)."""
        from pyannote.audio import Pipeline  # type: ignore
        import torch  # type: ignore

        self._pipeline = Pipeline.from_pretrained(
            self.PIPELINE_ID,
            use_auth_token=self._hf_token,
        )
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self._pipeline = self._pipeline.to(torch.device(device))
        self._loaded_flag = True

    async def unload(self) -> None:
        self._pipeline = None
        self._loaded_flag = False

    @property
    def is_loaded(self) -> bool:
        return self._loaded_flag

    async def diarize(
        self, segment: AudioSegment, job_id: str
    ) -> DiarizationResult:
        """Run diarization over *segment* and return typed result."""
        if not self._loaded_flag:
            await self.load()

        import asyncio
        import functools

        loop = asyncio.get_event_loop()

        def _run_sync() -> object:
            return self._pipeline(
                str(segment.processed_path),
                min_speakers=self._min_speakers,
                max_speakers=self._max_speakers,
            )

        annotation = await loop.run_in_executor(None, _run_sync)

        segments: list[DiarizationSegment] = []
        speaker_acc: dict[str, float] = {}

        for turn, _, speaker in annotation.itertracks(yield_label=True):
            seg = DiarizationSegment(
                speaker_id=speaker,
                start_seconds=turn.start,
                end_seconds=turn.end,
            )
            segments.append(seg)
            speaker_acc[speaker] = (
                speaker_acc.get(speaker, 0.0) + seg.duration
            )

        speakers = [
            Speaker(
                speaker_id=sp,
                total_speech_seconds=dur,
                segment_count=sum(
                    1 for s in segments if s.speaker_id == sp
                ),
            )
            for sp, dur in speaker_acc.items()
        ]

        return DiarizationResult(
            job_id=job_id,
            segments=segments,
            speakers=speakers,
            num_speakers=len(speakers),
            min_speakers=self._min_speakers,
            max_speakers=self._max_speakers,
        )
