import asyncio
from typing import List

import numpy as np

from app.ai.interfaces import (
    AudioData,
    ReconstructionInterface,
    SeparatedAudio,
)
from app.utils.logging import get_logger

logger = get_logger(__name__)


class AudioReconstructionService(ReconstructionInterface):
    async def reconstruct(
        self,
        separated: List[SeparatedAudio],
        selected_ids: List[str],
        original: AudioData,
    ) -> AudioData:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, self._reconstruct_sync, separated, selected_ids, original
        )
        logger.info(
            "reconstruction_complete",
            selected=selected_ids,
            output_duration=result.duration,
        )
        return result

    def _reconstruct_sync(
        self,
        separated: List[SeparatedAudio],
        selected_ids: List[str],
        original: AudioData,
    ) -> AudioData:
        selected_streams = [s for s in separated if s.speaker_id in selected_ids]

        if not selected_streams:
            silence = np.zeros(
                int(original.duration * original.sample_rate), dtype=np.float32
            )
            return AudioData(
                waveform=silence,
                sample_rate=original.sample_rate,
                duration=original.duration,
                file_path=original.file_path,
            )

        target_length = int(original.duration * original.sample_rate)
        mixed = np.zeros(target_length, dtype=np.float64)

        for stream in selected_streams:
            stream_data = stream.waveform.astype(np.float64)
            n = min(len(stream_data), target_length)
            mixed[:n] += stream_data[:n]

        peak = np.abs(mixed).max()
        if peak > 0:
            mixed = mixed / peak * 0.95

        duration = len(mixed) / original.sample_rate

        return AudioData(
            waveform=mixed.astype(np.float32),
            sample_rate=original.sample_rate,
            duration=duration,
            file_path=original.file_path,
        )
