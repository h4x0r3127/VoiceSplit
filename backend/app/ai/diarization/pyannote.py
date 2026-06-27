import asyncio
import io
from typing import List, Optional

import numpy as np

from app.ai.interfaces import (
    AudioData,
    DiarizationInterface,
    DiarizationSegment,
    VADSegment,
)
from app.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


class PyannoteDiarizationService(DiarizationInterface):
    def __init__(self) -> None:
        self._pipeline = None

    def _load_pipeline(self) -> None:
        if self._pipeline is not None:
            return

        from pyannote.audio import Pipeline

        self._pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=settings.HF_TOKEN,
        )
        logger.info("pyannote_pipeline_loaded")

    async def diarize(
        self, audio: AudioData, vad_segments: List[VADSegment]
    ) -> List[DiarizationSegment]:
        loop = asyncio.get_event_loop()
        segments = await loop.run_in_executor(None, self._diarize_sync, audio)
        logger.info("diarization_complete", segments=len(segments))
        return segments

    def _diarize_sync(self, audio: AudioData) -> List[DiarizationSegment]:
        import soundfile as sf
        import tempfile
        import os

        self._load_pipeline()

        waveform = audio.waveform
        if waveform.ndim == 1:
            waveform = waveform[np.newaxis, :]

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            sf.write(tmp_path, waveform.T, audio.sample_rate, subtype="PCM_16")
            diarization = self._pipeline(tmp_path)
        finally:
            os.unlink(tmp_path)

        segments: List[DiarizationSegment] = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append(
                DiarizationSegment(
                    start=turn.start,
                    end=turn.end,
                    speaker_label=speaker,
                )
            )

        segments.sort(key=lambda s: s.start)
        return segments
