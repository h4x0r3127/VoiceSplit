"""
Speaker embedding package for the VoiceSplit AI pipeline.

Exposes SpeakerEmbeddingService as the single public entry-point.
"""

from app.ai.embeddings.service import SpeakerEmbeddingService

__all__ = ["SpeakerEmbeddingService"]
