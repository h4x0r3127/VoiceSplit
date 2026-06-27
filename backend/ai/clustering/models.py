"""Strongly-typed Pydantic models for the speaker clustering stage."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SpeakerCluster(BaseModel):
    """One cluster representing a unique speaker."""

    cluster_id: int
    speaker_label: str  # e.g. "SPEAKER_00"
    member_count: int
    centroid: list[float]  # mean embedding vector
    intra_cluster_distance: float = Field(ge=0.0)


class ClusterResult(BaseModel):
    """Complete output of the clustering stage."""

    job_id: str
    clusters: list[SpeakerCluster]
    num_clusters: int
    algorithm: str = "spectral"
    silhouette_score: float = Field(default=-1.0, ge=-1.0, le=1.0)
    embedding_to_cluster: dict[int, int] = {}  # embedding index → cluster_id
