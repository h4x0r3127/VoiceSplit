"""Strongly-typed Pydantic models for the Voice Activity Detection stage."""

from __future__ import annotations

from pydantic import BaseModel, Field


class VoiceSegment(BaseModel):
    """A contiguous span of detected voice activity."""

    start_seconds: float = Field(ge=0.0)
    end_seconds: float = Field(ge=0.0)
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)

    @property
    def duration(self) -> float:
        return self.end_seconds - self.start_seconds


class VoiceActivity(BaseModel):
    """Aggregated VAD output for one audio file."""

    job_id: str
    speech_segments: list[VoiceSegment]
    silence_ratio: float = Field(ge=0.0, le=1.0)
    speech_ratio: float = Field(ge=0.0, le=1.0)
    total_speech_seconds: float
    total_duration_seconds: float


class VADResult(BaseModel):
    """Complete output of the VAD stage."""

    job_id: str
    activity: VoiceActivity
    model_name: str = "silero-vad"
    threshold_used: float = 0.5
