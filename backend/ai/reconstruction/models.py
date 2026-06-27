"""Strongly-typed Pydantic models for the audio reconstruction stage."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class ReconstructedSpeaker(BaseModel):
    """Audio reconstructed for a single, isolated speaker."""

    speaker_id: str
    audio_path: Path
    duration_seconds: float
    sample_rate: int
    num_segments_merged: int
    silence_padding_seconds: float = Field(ge=0.0, default=0.25)


class ReconstructionResult(BaseModel):
    """Complete output of the reconstruction stage."""

    job_id: str
    speakers: list[ReconstructedSpeaker]
    num_speakers: int
    total_processing_seconds: float
