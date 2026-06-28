"""
Speaker identity models for the VoiceSplit AI pipeline.

Provides Pydantic v2 models covering four stages of speaker identity
resolution:

1. **SpeakerEmbedding** — raw embedding extracted per diarization label.
2. **SpeakerCluster**  — merged / de-duplicated speaker after clustering.
3. **SpeakerPreview**  — lightweight card returned to the frontend for
   user confirmation before export.
4. **SpeakerProfile**  — full speaker record returned after the user
   confirms the diarization result.
"""

from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.ai.models.diarization import DiarizationSegment


class SpeakerEmbedding(BaseModel):
    """Raw speaker voice-print extracted by the embedding model.

    The ``embedding`` field holds a 192-dimensional numpy ``ndarray``
    produced by an ECAPA-TDNN model.  It is typed as ``Any`` to avoid
    importing numpy at module load time.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    speaker_label: str = Field(
        ..., description="Diarization speaker label this embedding belongs to, e.g. 'SPEAKER_00'."
    )
    embedding: Any = Field(
        ...,
        description=(
            "numpy ndarray of shape (192,) — ECAPA-TDNN speaker embedding vector. "
            "Typed as Any to avoid a hard numpy import."
        ),
    )
    embedding_dim: int = Field(
        ..., gt=0, description="Dimensionality of the embedding vector (typically 192)."
    )
    segments: List[DiarizationSegment] = Field(
        default_factory=list,
        description="All diarization segments attributed to this speaker label.",
    )
    total_speaking_time: float = Field(
        ..., ge=0.0, description="Total seconds the speaker was active across all segments."
    )


class SpeakerCluster(BaseModel):
    """Speaker identity after agglomerative clustering of raw embeddings.

    Clustering resolves cases where the diarizer over-segments and assigns
    multiple labels to the same physical speaker.  The ``embedding`` field
    is the centroid of all embeddings assigned to this cluster.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    cluster_id: str = Field(
        ...,
        description="Stable cluster identifier, e.g. 'speaker_0', 'speaker_1'.",
    )
    color: str = Field(
        ...,
        description=(
            "Hex colour string from the VoiceSplit brand palette assigned to "
            "this speaker for UI display, e.g. '#3B82F6'."
        ),
    )
    embedding: Any = Field(
        ...,
        description=(
            "Centroid numpy ndarray of shape (192,) representing the average "
            "voice-print of all speakers merged into this cluster."
        ),
    )
    segments: List[DiarizationSegment] = Field(
        default_factory=list,
        description="All diarization segments attributed to this cluster.",
    )
    speaking_duration: float = Field(
        ..., ge=0.0, description="Total speaking time for this cluster in seconds."
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Mean clustering confidence across all segments."
    )


class SpeakerPreview(BaseModel):
    """Lightweight speaker card shown to the user before they confirm export.

    Contains only data needed to render a speaker tile in the UI —
    no embedding vectors.  The ``preview_url`` is a presigned URL that
    expires after one hour.
    """

    speaker_id: str = Field(..., description="Cluster identifier, e.g. 'speaker_0'.")
    label: str = Field(..., description="Human-readable label shown in the UI, e.g. 'Speaker 1'.")
    color: str = Field(..., description="Hex colour string assigned to this speaker.")
    speaking_duration: float = Field(
        ..., ge=0.0, description="Total speaking time in seconds."
    )
    segment_count: int = Field(..., ge=0, description="Number of speech segments for this speaker.")
    preview_s3_key: Optional[str] = Field(
        default=None,
        description="Object storage key for the short audio preview clip.",
    )
    preview_url: Optional[str] = Field(
        default=None,
        description="Presigned URL for the preview clip; expires after 1 hour.",
    )
    gender: Optional[str] = Field(
        default=None, description="Predicted gender label, e.g. 'male', 'female'."
    )
    language: Optional[str] = Field(
        default=None, description="BCP-47 language code detected for this speaker, e.g. 'en-US'."
    )


class SpeakerProfile(BaseModel):
    """Full speaker record returned to the frontend after the user confirms diarization.

    Extends :class:`SpeakerPreview` with analytics fields computed during
    the metadata analysis stage.
    """

    speaker_id: str = Field(..., description="Cluster identifier, e.g. 'speaker_0'.")
    label: str = Field(..., description="Human-readable display label, e.g. 'Speaker 1'.")
    color: str = Field(..., description="Hex colour string assigned to this speaker.")
    speaking_duration: float = Field(
        ..., ge=0.0, description="Total speaking time in seconds."
    )
    speaking_percentage: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Percentage of total audio duration this speaker was active.",
    )
    segment_count: int = Field(..., ge=0, description="Number of speech segments.")
    preview: Optional[SpeakerPreview] = Field(
        default=None, description="Preview card for this speaker, if generated."
    )
    gender: Optional[str] = Field(default=None, description="Predicted gender label.")
    language: Optional[str] = Field(
        default=None, description="BCP-47 language code detected for this speaker."
    )
    emotion: Optional[str] = Field(
        default=None, description="Dominant emotion label, e.g. 'neutral', 'happy'."
    )
    accent: Optional[str] = Field(
        default=None, description="Detected accent or regional variety, e.g. 'British English'."
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall confidence of the speaker identity assignment.",
    )
