"""Strongly-typed Pydantic models for the metadata extraction stage."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class FileMetadata(BaseModel):
    """Low-level file and codec information extracted via FFprobe."""

    file_path: Path
    file_size_bytes: int = Field(ge=0)
    format_name: str
    duration_seconds: float
    bit_rate: int
    sample_rate: int
    channels: int
    codec_name: str
    has_video: bool = False


class SpeakerStats(BaseModel):
    """Per-speaker statistics derived from diarization output."""

    speaker_id: str
    speaking_time_seconds: float
    speaking_fraction: float = Field(ge=0.0, le=1.0)
    num_turns: int


class AudioMetadataResult(BaseModel):
    """Complete output of the metadata extraction stage."""

    job_id: str
    file_metadata: FileMetadata
    speaker_stats: list[SpeakerStats]
    total_speakers: int
    dominant_speaker_id: Optional[str] = None
    language_detected: Optional[str] = None
