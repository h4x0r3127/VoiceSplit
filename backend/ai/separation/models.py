"""Strongly-typed Pydantic models for the source separation stage."""

from __future__ import annotations

from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field


class StemType(str, Enum):
    VOCALS = "vocals"
    DRUMS = "drums"
    BASS = "bass"
    OTHER = "other"
    FULL_MIX = "full_mix"


class StemOutput(BaseModel):
    """One separated stem produced by Demucs."""

    stem_type: StemType
    output_path: Path
    sample_rate: int
    duration_seconds: float
    file_size_bytes: int = Field(ge=0)


class SeparationResult(BaseModel):
    """Complete output of the source separation stage."""

    job_id: str
    stems: list[StemOutput]
    model_name: str = "htdemucs"
    segments: int = 1  # number of Demucs chunks processed
    vocal_stem_path: Path | None = None

    def get_stem(self, stem_type: StemType) -> StemOutput | None:
        for s in self.stems:
            if s.stem_type == stem_type:
                return s
        return None
