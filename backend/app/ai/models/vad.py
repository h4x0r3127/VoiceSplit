"""
Voice Activity Detection (VAD) result models for the VoiceSplit AI pipeline.

Provides Pydantic v2 models that represent the output of the VAD stage —
timestamped speech segments used to filter silence before diarization.
"""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field, computed_field


class VADSegment(BaseModel):
    """A single contiguous speech region detected by the VAD model.

    All time values are expressed in seconds relative to the start of the
    original audio file.
    """

    start: float = Field(..., ge=0.0, description="Segment start time in seconds.")
    end: float = Field(..., ge=0.0, description="Segment end time in seconds.")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Model confidence that this region contains speech."
    )

    @computed_field  # type: ignore[misc]
    @property
    def duration(self) -> float:
        """Duration of this speech segment in seconds."""
        return self.end - self.start


class VADResult(BaseModel):
    """Aggregated output of a complete VAD pass over a single audio file.

    Provides both the raw segments and derived statistics so downstream
    stages can decide how to handle the recording (e.g. skip if nearly
    all silence).
    """

    segments: List[VADSegment] = Field(
        default_factory=list,
        description="Ordered list of detected speech segments.",
    )
    total_speech_duration: float = Field(
        ..., ge=0.0, description="Sum of all speech segment durations in seconds."
    )
    total_silence_duration: float = Field(
        ..., ge=0.0, description="Total silence / non-speech duration in seconds."
    )
    speech_ratio: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Fraction of total audio that contains speech (speech / total).",
    )
    processing_time_ms: float = Field(
        ..., ge=0.0, description="Wall-clock time taken to run VAD inference in milliseconds."
    )
