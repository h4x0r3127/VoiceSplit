"""
Speaker diarization result models for the VoiceSplit AI pipeline.

Provides Pydantic v2 models representing the output of the diarization stage —
time-stamped segments annotated with speaker labels such as ``SPEAKER_00``.
"""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field, computed_field


class DiarizationSegment(BaseModel):
    """A single time segment attributed to one speaker by the diarization model.

    Speaker labels follow the convention ``SPEAKER_<NN>`` (zero-padded two
    digits) as produced by pyannote.audio.  All time values are in seconds.
    """

    start: float = Field(..., ge=0.0, description="Segment start time in seconds.")
    end: float = Field(..., ge=0.0, description="Segment end time in seconds.")
    speaker_label: str = Field(
        ...,
        description="Speaker label assigned by the diarizer, e.g. 'SPEAKER_00'.",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Diarization model confidence score for this assignment.",
    )

    @computed_field  # type: ignore[misc]
    @property
    def duration(self) -> float:
        """Duration of this diarization segment in seconds."""
        return self.end - self.start


class DiarizationResult(BaseModel):
    """Complete output of a diarization pass over a single audio file.

    Contains an ordered list of segments and derived statistics used by the
    embedding and clustering stages.
    """

    segments: List[DiarizationSegment] = Field(
        default_factory=list,
        description="Chronologically ordered list of speaker-labelled segments.",
    )
    num_speakers: int = Field(
        ..., ge=0, description="Number of distinct speaker labels detected."
    )
    speaker_labels: List[str] = Field(
        default_factory=list,
        description="Unique speaker labels found in the segments list.",
    )
    total_duration: float = Field(
        ..., ge=0.0, description="Total duration covered by all segments in seconds."
    )
    processing_time_ms: float = Field(
        ..., ge=0.0, description="Wall-clock inference time in milliseconds."
    )
