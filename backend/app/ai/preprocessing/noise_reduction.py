import asyncio

import numpy as np
import noisereduce as nr

from app.ai.interfaces import AudioData, NoiseReductionInterface
from app.utils.logging import get_logger

logger = get_logger(__name__)


class NoiseReductionService(NoiseReductionInterface):
    def __init__(self, stationary: bool = False, prop_decrease: float = 0.75) -> None:
        self._stationary = stationary
        self._prop_decrease = prop_decrease

    async def reduce(self, audio: AudioData) -> AudioData:
        loop = asyncio.get_event_loop()
        cleaned = await loop.run_in_executor(None, self._reduce_sync, audio)
        logger.info("noise_reduction_complete", path=audio.file_path)
        return cleaned

    def _reduce_sync(self, audio: AudioData) -> AudioData:
        waveform = audio.waveform

        if waveform.ndim == 1:
            cleaned = nr.reduce_noise(
                y=waveform,
                sr=audio.sample_rate,
                stationary=self._stationary,
                prop_decrease=self._prop_decrease,
            )
        else:
            channels = []
            for ch in range(waveform.shape[0]):
                cleaned_ch = nr.reduce_noise(
                    y=waveform[ch],
                    sr=audio.sample_rate,
                    stationary=self._stationary,
                    prop_decrease=self._prop_decrease,
                )
                channels.append(cleaned_ch)
            cleaned = np.stack(channels, axis=0)

        return AudioData(
            waveform=cleaned.astype(np.float32),
            sample_rate=audio.sample_rate,
            duration=audio.duration,
            file_path=audio.file_path,
        )
