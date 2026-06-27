"""Strongly-typed Pydantic models for the transcription stage."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class TranscriptWord(BaseModel):
    """Word-level alignment from Whisper word timestamps."""

    word: str
    start_seconds: float = Field(ge=0.0)
    end_seconds: float = Field(ge=0.0)
    probability: float = Field(ge=0.0, le=1.0, default=1.0)


class TranscriptSegment(BaseModel):
    """One transcribed segment attributed to a speaker."""

    speaker_id: Optional[str] = None
    start_seconds: float = Field(ge=0.0)
    end_seconds: float = Field(ge=0.0)
    text: str
    language: str = "en"
    avg_logprob: float = 0.0
    no_speech_prob: float = Field(ge=0.0, le=1.0, default=0.0)
    words: list[TranscriptWord] = []


class TranscriptionResult(BaseModel):
    """Complete output of the transcription stage."""

    job_id: str
    segments: list[TranscriptSegment]
    language: str
    model_name: str = "openai/whisper-large-v3"
    full_text: str = ""
    duration_seconds: float
