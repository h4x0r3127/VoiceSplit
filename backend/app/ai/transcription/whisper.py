import asyncio
import os
import tempfile
from typing import List, Optional

import numpy as np
import torch

from app.ai.interfaces import (
    AudioData,
    SpeakerCluster,
    TranscriptionInterface,
    TranscriptSegment,
)
from app.utils.logging import get_logger

logger = get_logger(__name__)


class WhisperTranscriptionService(TranscriptionInterface):
    def __init__(self, model_size: str = "large-v3") -> None:
        self._model_size = model_size
        self._model = None

    def _load_model(self) -> None:
        if self._model is not None:
            return
        import whisper

        self._model = whisper.load_model(self._model_size)
        logger.info("whisper_model_loaded", size=self._model_size)

    async def transcribe(
        self, audio: AudioData, clusters: List[SpeakerCluster]
    ) -> List[TranscriptSegment]:
        loop = asyncio.get_event_loop()
        segments = await loop.run_in_executor(
            None, self._transcribe_sync, audio, clusters
        )
        logger.info("transcription_complete", segments=len(segments))
        return segments

    def _transcribe_sync(
        self, audio: AudioData, clusters: List[SpeakerCluster]
    ) -> List[TranscriptSegment]:
        import soundfile as sf

        self._load_model()

        waveform = audio.waveform
        sr = audio.sample_rate

        all_segments: List[TranscriptSegment] = []

        for cluster in clusters:
            for seg in cluster.segments:
                start_sample = int(seg.start * sr)
                end_sample = int(seg.end * sr)
                chunk = waveform[start_sample:end_sample]

                if len(chunk) < sr * 0.3:
                    continue

                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp_path = tmp.name

                try:
                    sf.write(tmp_path, chunk, sr, subtype="PCM_16")
                    result = self._model.transcribe(
                        tmp_path,
                        word_timestamps=True,
                        verbose=False,
                    )
                finally:
                    os.unlink(tmp_path)

                for whisper_seg in result.get("segments", []):
                    text = whisper_seg.get("text", "").strip()
                    if not text:
                        continue

                    all_segments.append(
                        TranscriptSegment(
                            start=seg.start + whisper_seg.get("start", 0),
                            end=seg.start + whisper_seg.get("end", 0),
                            speaker_id=cluster.cluster_id,
                            text=text,
                            confidence=float(
                                np.exp(whisper_seg.get("avg_logprob", -1))
                            ),
                        )
                    )

        all_segments.sort(key=lambda s: s.start)
        return all_segments
