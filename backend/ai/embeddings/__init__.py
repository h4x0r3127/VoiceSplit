"""Embeddings module public surface."""

from .models import EmbeddingResult, SpeakerEmbedding
from .service import EmbeddingService

__all__ = ["EmbeddingResult", "EmbeddingService", "SpeakerEmbedding"]
