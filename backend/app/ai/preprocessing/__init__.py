"""
Preprocessing package for the VoiceSplit AI pipeline.

Exposes AudioPreprocessorService as the single public entry-point for all
audio loading, normalisation, and noise-reduction operations.
"""

from app.ai.preprocessing.service import AudioPreprocessorService

__all__ = ["AudioPreprocessorService"]
