"""
AudioResampler — changes sample rate and channel count via FFmpeg.

Kept separate from AudioLoader so each class has exactly one reason to change
(SRP), and new resampling backends (e.g. librosa) can be swapped in without
touching loading or normalisation logic.
"""

from __future__ import annotations

import asyncio
import shutil
from pathlib import Path
from typing import Optional

from .models import AudioInput, AudioSegment


class AudioResampler:
    """Resamples an AudioSegment to the target sample rate / channel count."""

    async def resample(
        self,
        segment: AudioSegment,
        input: AudioInput,
    ) -> tuple[AudioSegment, bool, Optional[int], Optional[int]]:
        """Resample *segment* if its SR or channels differ from *input* targets.

        Returns
        -------
        (resampled_segment, was_converted, original_sr, original_channels)
        """
        needs_conversion = (
            segment.sample_rate != input.sample_rate_target
            or segment.channels != input.channels_target
        )

        if not needs_conversion:
            return segment, False, None, None

        orig_sr = segment.sample_rate
        orig_ch = segment.channels

        out_path = segment.processed_path.parent / (
            segment.processed_path.stem + "_resampled.wav"
        )

        cmd = [
            "ffmpeg", "-y",
            "-i", str(segment.processed_path),
            "-ar", str(input.sample_rate_target),
            "-ac", str(input.channels_target),
            str(out_path),
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"Resampling failed: {stderr.decode()}")

        resampled = segment.model_copy(
            update={
                "sample_rate": input.sample_rate_target,
                "channels": input.channels_target,
                "processed_path": out_path,
            }
        )
        return resampled, True, orig_sr, orig_ch
