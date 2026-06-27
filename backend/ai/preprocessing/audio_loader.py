"""
AudioLoader — decodes audio/video files to an in-memory AudioSegment.

Internally invokes FFmpeg via subprocess for universal format support.
Keeping this class separate from the resampler and normalizer follows
the Single Responsibility Principle.
"""

from __future__ import annotations

import asyncio
import subprocess
import tempfile
from pathlib import Path

from .models import AudioFormat, AudioInput, AudioSegment


class AudioLoader:
    """Decodes any audio or video file to 16-bit PCM WAV via FFmpeg."""

    async def load(self, input: AudioInput) -> AudioSegment:
        """Decode *input.file_path* to a normalised WAV in a temp directory.

        Returns
        -------
        AudioSegment
            Decoded (but not yet resampled or amplitude-normalised) segment.
        """
        tmp_dir = Path(tempfile.mkdtemp(prefix="vs_load_"))
        out_path = tmp_dir / f"{input.job_id}_raw.wav"

        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-i", str(input.file_path),
            "-vn",                        # drop video stream
            "-acodec", "pcm_s16le",
            "-ar", str(input.sample_rate_target),
            "-ac", str(input.channels_target),
            str(out_path),
        ]

        proc = await asyncio.create_subprocess_exec(
            *ffmpeg_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()

        if proc.returncode != 0:
            raise RuntimeError(
                f"FFmpeg failed (exit {proc.returncode}): {stderr.decode()}"
            )

        # Probe duration & amplitude stats
        duration, peak, rms = await self._probe_wav(out_path)
        num_samples = int(duration * input.sample_rate_target)

        return AudioSegment(
            job_id=input.job_id,
            sample_rate=input.sample_rate_target,
            channels=input.channels_target,
            duration_seconds=duration,
            num_samples=num_samples,
            format=AudioFormat.WAV,
            processed_path=out_path,
            peak_amplitude=peak,
            rms_amplitude=rms,
        )

    async def _probe_wav(self, path: Path) -> tuple[float, float, float]:
        """Return (duration_s, peak, rms) using FFprobe."""
        cmd = [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_streams", "-show_format",
            str(path),
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()

        import json
        data = json.loads(stdout.decode())
        duration = float(data.get("format", {}).get("duration", 0.0))
        # Amplitude stats require a full decode pass; use safe defaults here.
        # In production, add an astats filter pass for exact peak/rms.
        return duration, 1.0, 0.1
