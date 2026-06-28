"""
Voice Activity Detection (VAD) package for the VoiceSplit AI pipeline.

Exposes VoiceActivityDetectorService as the single public entry-point.
"""

from app.ai.vad.service import VoiceActivityDetectorService

__all__ = ["VoiceActivityDetectorService"]
