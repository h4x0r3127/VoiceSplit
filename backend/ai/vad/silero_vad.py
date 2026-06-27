"""
SileroVAD — concrete driver wrapping the Silero VAD model.

Model details: https://github.com/snakers4/silero-vad
Kept separate from VADService so the model backend can be swapped to
WebRTC VAD or any future model without changing the service interface.
"""

from __future__ import annotations

from ai.interfaces.protocols import ILoadable
from ai.preprocessing.models import AudioSegment
from .models import VADResult, VoiceActivity, VoiceSegment


class SileroVAD(ILoadable):
    """Wraps the Silero VAD PyTorch model for speech/silence detection."""

    MODEL_REPO = "snakers4/silero-vad"

    def __init__(self, threshold: float = 0.5) -> None:
        self._threshold = threshold
        self._model = None
        self._utils = None
        self._loaded_flag = False

    async def load(self) -> None:
        """Lazy-load Silero VAD from Torch Hub (downloads once, cached)."""
        import torch  # type: ignore

        self._model, self._utils = torch.hub.load(
            repo_or_dir=self.MODEL_REPO,
            model="silero_vad",
            force_reload=False,
            onnx=False,
        )
        self._model.eval()
        self._loaded_flag = True

    async def unload(self) -> None:
        self._model = None
        self._utils = None
        self._loaded_flag = False

    @property
    def is_loaded(self) -> bool:
        return self._loaded_flag

    async def detect(
        self, segment: AudioSegment, job_id: str
    ) -> VADResult:
        """Run VAD inference over *segment*.

        Returns
        -------
        VADResult
            Detected speech segments with timestamps.
        """
        if not self._loaded_flag:
            await self.load()

        import torch
        import torchaudio  # type: ignore

        wav, sr = torchaudio.load(str(segment.processed_path))
        if sr != 16_000:
            resampler = torchaudio.transforms.Resample(sr, 16_000)
            wav = resampler(wav)

        get_speech_ts = self._utils[0]
        speech_timestamps = get_speech_ts(
            wav.squeeze(0),
            self._model,
            threshold=self._threshold,
            sampling_rate=16_000,
        )

        voice_segments = [
            VoiceSegment(
                start_seconds=ts["start"] / 16_000,
                end_seconds=ts["end"] / 16_000,
            )
            for ts in speech_timestamps
        ]

        total_speech = sum(s.duration for s in voice_segments)
        total_dur = segment.duration_seconds or 1e-6

        activity = VoiceActivity(
            job_id=job_id,
            speech_segments=voice_segments,
            speech_ratio=min(total_speech / total_dur, 1.0),
            silence_ratio=max(1.0 - total_speech / total_dur, 0.0),
            total_speech_seconds=total_speech,
            total_duration_seconds=total_dur,
        )

        return VADResult(
            job_id=job_id,
            activity=activity,
            threshold_used=self._threshold,
        )
