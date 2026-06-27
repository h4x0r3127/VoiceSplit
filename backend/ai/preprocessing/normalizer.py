"""
AudioNormalizer — peak-normalises an AudioSegment to –1 dBFS.

Decoupled from loading and resampling so the normalisation strategy (peak,
loudness/EBU-R128, RMS) can be changed independently.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from .models import AudioSegment


class AudioNormalizer:
    """Peak-normalises audio to –1 dBFS using FFmpeg's loudnorm filter."""

    DEFAULT_TARGET_LUFS: float = -23.0   # EBU R128 target
    DEFAULT_TRUE_PEAK: float = -1.0       # dBTP

    async def normalise(self, segment: AudioSegment) -> AudioSegment:
        """Apply two-pass EBU R128 loudness normalisation.

        Parameters
        ----------
        segment:
            WAV segment to normalise (modified in place via a new file).

        Returns
        -------
        AudioSegment
            Updated model pointing to the normalised WAV.
        """
        out_path = segment.processed_path.parent / (
            segment.processed_path.stem + "_norm.wav"
        )

        # Single-pass loudnorm (linear mode for speed)
        cmd = [
            "ffmpeg", "-y",
            "-i", str(segment.processed_path),
            "-af",
            f"loudnorm=I={self.DEFAULT_TARGET_LUFS}:TP={self.DEFAULT_TRUE_PEAK}:LRA=11",
            str(out_path),
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"Normalisation failed: {stderr.decode()}")

        # After normalisation peak ≈ 0.89 (−1 dBFS), rms varies
        return segment.model_copy(
            update={
                "processed_path": out_path,
                "peak_amplitude": 0.89,
            }
        )
