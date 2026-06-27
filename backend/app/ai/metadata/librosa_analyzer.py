import asyncio
from typing import List

import numpy as np

from app.ai.interfaces import (
    AudioData,
    AudioMetadata,
    MetadataInterface,
    SeparatedAudio,
)
from app.utils.logging import get_logger

logger = get_logger(__name__)

_EMOTION_RULES = [
    ("excited", lambda pv, em: pv > 0.05 and em > 0.08),
    ("angry", lambda pv, em: pv > 0.04 and em > 0.06),
    ("happy", lambda pv, em: pv > 0.03 and em > 0.04),
    ("sad", lambda pv, em: pv < 0.01 and em < 0.03),
    ("calm", lambda pv, em: True),
]


def _classify_emotion(pitch_variance: float, energy_mean: float) -> str:
    for label, condition in _EMOTION_RULES:
        if condition(pitch_variance, energy_mean):
            return label
    return "neutral"


class LibrosaMetadataService(MetadataInterface):
    async def analyze(
        self, audio: AudioData, separated: List[SeparatedAudio]
    ) -> AudioMetadata:
        loop = asyncio.get_event_loop()
        metadata = await loop.run_in_executor(None, self._analyze_sync, audio)
        logger.info("metadata_analysis_complete")
        return metadata

    def _analyze_sync(self, audio: AudioData) -> AudioMetadata:
        import librosa

        y = audio.waveform
        sr = audio.sample_rate

        if y.ndim > 1:
            y = y.mean(axis=0)

        y = y.astype(np.float32)

        tempo_arr, _ = librosa.beat.beat_track(y=y, sr=sr)
        tempo = float(tempo_arr) if np.ndim(tempo_arr) == 0 else float(tempo_arr[0])

        pitches, magnitudes = librosa.piptrack(y=y, sr=sr, threshold=0.1)
        pitch_values = pitches[magnitudes > np.median(magnitudes)]
        pitch_mean = float(np.mean(pitch_values)) if len(pitch_values) > 0 else 0.0
        pitch_variance = float(np.var(pitch_values)) if len(pitch_values) > 0 else 0.0

        rms = librosa.feature.rms(y=y)
        energy_mean = float(np.mean(rms))

        non_silent = librosa.effects.split(y, top_db=30)
        total_speech_s = sum((end - start) / sr for start, end in non_silent)
        pause_duration_total = max(0.0, audio.duration - total_speech_s)

        speaking_rate = 0.0
        if total_speech_s > 0:
            speaking_rate = audio.duration / total_speech_s

        dominant_emotion = _classify_emotion(pitch_variance, energy_mean)

        return AudioMetadata(
            tempo=tempo,
            pitch_mean=pitch_mean,
            energy_mean=energy_mean,
            speaking_rate=speaking_rate,
            pause_duration_total=pause_duration_total,
            dominant_emotion=dominant_emotion,
        )
