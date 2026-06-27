"""Strongly-typed Pydantic models for the preprocessing stage."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class AudioFormat(str, Enum):
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    OGG = "ogg"
    M4A = "m4a"
    WEBM = "webm"
    MP4 = "mp4"  # video container
    MKV = "mkv"  # video container


class AudioInput(BaseModel):
    """Raw input supplied by the caller (path to the uploaded file)."""

    file_path: Path
    original_filename: str
    job_id: str
    sample_rate_target: int = Field(default=16_000, ge=8_000, le=48_000)
    channels_target: int = Field(default=1, ge=1, le=2)

    @field_validator("file_path")
    @classmethod
    def path_must_exist(cls, v: Path) -> Path:
        if not v.exists():
            raise ValueError(f"Audio file not found: {v}")
        return v


class AudioSegment(BaseModel):
    """A normalised, resampled audio segment ready for AI processing."""

    job_id: str
    sample_rate: int
    channels: int
    duration_seconds: float
    num_samples: int
    format: AudioFormat
    # Absolute path to the processed WAV file on the worker filesystem
    processed_path: Path
    peak_amplitude: float = Field(ge=0.0, le=1.0)
    rms_amplitude: float = Field(ge=0.0, le=1.0)


class PreprocessingResult(BaseModel):
    """Complete output of the preprocessing stage."""

    job_id: str
    segment: AudioSegment
    was_converted: bool = False
    original_sample_rate: Optional[int] = None
    original_channels: Optional[int] = None
    ffmpeg_command: Optional[str] = None
