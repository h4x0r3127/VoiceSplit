import asyncio
from typing import List, Optional

import numpy as np
import torch

from app.ai.interfaces import AudioData, VADInterface, VADSegment
from app.utils.logging import get_logger

logger = get_logger(__name__)

_MIN_DURATION_MS = 250


class SileroVADService(VADInterface):
    def __init__(self, threshold: float = 0.5, min_duration_ms: int = _MIN_DURATION_MS) -> None:
        self._threshold = threshold
        self._min_duration_ms = min_duration_ms
        self._model: Optional[torch.nn.Module] = None
        self._get_timestamps = None

    def _load_model(self) -> None:
        if self._model is not None:
            return
        model, utils = torch.hub.load(
            repo_or_dir="snakers4/silero-vad",
            model="silero_vad",
            force_reload=False,
            onnx=False,
        )
        self._model = model
        (
            self._get_timestamps,
            _,
            _,
            _,
            _,
        ) = utils
        logger.info("silero_vad_model_loaded")

    async def detect(self, audio: AudioData) -> List[VADSegment]:
        loop = asyncio.get_event_loop()
        segments = await loop.run_in_executor(None, self._detect_sync, audio)
        logger.info("vad_detection_complete", segments=len(segments))
        return segments

    def _detect_sync(self, audio: AudioData) -> List[VADSegment]:
        self._load_model()

        waveform = audio.waveform
        if waveform.ndim > 1:
            waveform = waveform.mean(axis=0)

        tensor = torch.FloatTensor(waveform)

        timestamps = self._get_timestamps(
            tensor,
            self._model,
            threshold=self._threshold,
            sampling_rate=audio.sample_rate,
            min_speech_duration_ms=self._min_duration_ms,
        )

        min_duration_s = self._min_duration_ms / 1000.0
        segments: List[VADSegment] = []
        for ts in timestamps:
            start = ts["start"] / audio.sample_rate
            end = ts["end"] / audio.sample_rate
            if (end - start) >= min_duration_s:
                segments.append(VADSegment(start=start, end=end, confidence=1.0))

        return segments
