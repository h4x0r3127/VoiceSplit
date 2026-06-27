"""Strongly-typed Pydantic models for the export stage."""

from __future__ import annotations

from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field


class ExportFormat(str, Enum):
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    OGG = "ogg"


class SpeakerExport(BaseModel):
    """One exported audio file for a single isolated speaker."""

    speaker_id: str
    export_path: Path
    format: ExportFormat
    duration_seconds: float
    file_size_bytes: int = Field(ge=0)
    bit_rate: Optional[int] = None
    sample_rate: int = 16_000
    storage_key: Optional[str] = None   # S3 / MinIO object key after upload

    from typing import Optional


class ExportResult(BaseModel):
    """Complete output of the export stage."""

    job_id: str
    exports: list[SpeakerExport]
    format: ExportFormat
    transcript_path: Optional[Path] = None  # path to SRT / VTT file if produced
    num_speakers_exported: int
    total_export_size_bytes: int

    from typing import Optional
