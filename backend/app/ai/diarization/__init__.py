"""
Speaker diarization package for the VoiceSplit AI pipeline.

Exposes SpeakerDiarizationService as the single public entry-point.
"""

from app.ai.diarization.service import SpeakerDiarizationService

__all__ = ["SpeakerDiarizationService"]
