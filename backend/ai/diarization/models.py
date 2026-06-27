"""Strongly-typed Pydantic models for the speaker diarization stage."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Speaker(BaseModel):
    """A uniquely identified speaker in the audio."""

    speaker_id: str  # e.g. "SPEAKER_00"
    total_speech_seconds: float
    segment_count: int


class DiarizationSegment(BaseModel):
    """One speaker's continuous speech segment."""

    speaker_id: str
    start_seconds: float = Field(ge=0.0)
    end_seconds: float = Field(ge=0.0)
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)

    @property
    def duration(self) -> float:
        return self.end_seconds - self.start_seconds


class DiarizationResult(BaseModel):
    """Complete output of the diarization stage."""

    job_id: str
    segments: list[DiarizationSegment]
    speakers: list[Speaker]
    num_speakers: int
    model_name: str = "pyannote/speaker-diarization-3.1"
    min_speakers: int = 1
    max_speakers: int = 8
