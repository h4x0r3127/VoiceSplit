"""Strongly-typed Pydantic models for the speaker embeddings stage."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SpeakerEmbedding(BaseModel):
    """D-vector / x-vector embedding for one speaker segment."""

    speaker_id: str
    segment_start: float
    segment_end: float
    embedding: list[float]  # dimension determined by chosen encoder
    embedding_dim: int

    @property
    def norm(self) -> float:
        import math
        return math.sqrt(sum(x * x for x in self.embedding))


class EmbeddingResult(BaseModel):
    """Complete output of the speaker embedding stage."""

    job_id: str
    embeddings: list[SpeakerEmbedding]
    model_name: str = "pyannote/embedding"
    embedding_dim: int
    num_segments_embedded: int
