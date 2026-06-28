"""
Transcription result models for the VoiceSplit AI pipeline.

Provides Pydantic v2 models for word-level and segment-level transcriptions
produced by the Whisper large-v3 model, annotated with speaker attribution
from the diarization / clustering stages.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class TranscriptWord(BaseModel):
    """A single word with sub-second timing and confidence metadata.

    Produced by Whisper's word-level timestamp mode.  All time values
    are in seconds relative to the start of the audio file.
    """

    word: str = Field(..., description="The recognised word token.")
    start: float = Field(..., ge=0.0, description="Word start time in seconds.")
    end: float = Field(..., ge=0.0, description="Word end time in seconds.")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Per-word ASR confidence score."
    )


class TranscriptSegment(BaseModel):
    """A speaker-attributed transcription segment.

    Each segment corresponds to a continuous speech turn by a single
    speaker.  It contains the full text for that turn as well as optional
    word-level timing data.
    """

    segment_id: str = Field(
        ..., description="Unique identifier for this transcript segment (UUID4)."
    )
    speaker_id: str = Field(
        ..., description="Cluster identifier of the speaker, e.g. 'speaker_0'."
    )
    speaker_label: str = Field(
        ..., description="Human-readable speaker label shown in the UI, e.g. 'Speaker 1'."
    )
    speaker_color: str = Field(
        ..., description="Hex colour string assigned to the speaker for UI display."
    )
    start: float = Field(..., ge=0.0, description="Segment start time in seconds.")
    end: float = Field(..., ge=0.0, description="Segment end time in seconds.")
    text: str = Field(..., description="Full transcribed text for this speech turn.")
    words: List[TranscriptWord] = Field(
        default_factory=list,
        description="Word-level tokens with timestamps; empty when word timestamps are disabled.",
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Mean confidence score for this segment."
    )
    language: Optional[str] = Field(
        default=None,
        description="BCP-47 language code detected for this segment, e.g. 'en'.",
    )


class TranscriptResult(BaseModel):
    """Complete transcription output for a single audio file.

    Aggregates all :class:`TranscriptSegment` instances together with
    document-level statistics required by the export stage.
    """

    segments: List[TranscriptSegment] = Field(
        default_factory=list,
        description="Chronologically ordered list of speaker-attributed transcript segments.",
    )
    full_text: str = Field(
        ...,
        description=(
            "Concatenated plain-text transcript of the entire recording, "
            "with speaker labels inlined."
        ),
    )
    language: str = Field(
        ...,
        description="BCP-47 language code of the predominant language in the recording.",
    )
    total_duration: float = Field(
        ..., ge=0.0, description="Total duration of the transcribed audio in seconds."
    )
    word_count: int = Field(..., ge=0, description="Total number of word tokens in the transcript.")
    processing_time_ms: float = Field(
        ..., ge=0.0, description="Wall-clock time taken for transcription inference in milliseconds."
    )
