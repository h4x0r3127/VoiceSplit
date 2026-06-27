import asyncio
import os

import numpy as np

from app.ai.interfaces import AudioData, AudioLoaderInterface
from app.utils.logging import get_logger

logger = get_logger(__name__)


class AudioLoaderService(AudioLoaderInterface):
    def __init__(self, target_sample_rate: int = 16000, mono: bool = True) -> None:
        self._target_sample_rate = target_sample_rate
        self._mono = mono

    async def load(self, file_path: str) -> AudioData:
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        loop = asyncio.get_event_loop()
        waveform, sample_rate, duration = await loop.run_in_executor(
            None, self._load_sync, file_path
        )
        logger.info(
            "audio_loaded",
            path=file_path,
            sample_rate=sample_rate,
            duration=duration,
            shape=waveform.shape,
        )
        return AudioData(
            waveform=waveform,
            sample_rate=sample_rate,
            duration=duration,
            file_path=file_path,
        )

    def _load_sync(self, file_path: str) -> tuple[np.ndarray, int, float]:
        import torchaudio
        import torchaudio.transforms as T

        waveform_tensor, sample_rate = torchaudio.load(file_path)

        if self._mono and waveform_tensor.shape[0] > 1:
            waveform_tensor = waveform_tensor.mean(dim=0, keepdim=True)

        if sample_rate != self._target_sample_rate:
            resampler = T.Resample(orig_freq=sample_rate, new_freq=self._target_sample_rate)
            waveform_tensor = resampler(waveform_tensor)
            sample_rate = self._target_sample_rate

        waveform_np = waveform_tensor.squeeze().numpy()
        duration = len(waveform_np) / sample_rate
        return waveform_np, sample_rate, duration
