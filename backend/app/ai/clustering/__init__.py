"""
Speaker clustering package for the VoiceSplit AI pipeline.

Exposes SpeakerClusterService as the single public entry-point.
"""

from app.ai.clustering.service import SpeakerClusterService

__all__ = ["SpeakerClusterService"]
