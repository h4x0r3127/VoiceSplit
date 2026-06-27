"""Metadata module public surface."""

from .models import AudioMetadataResult, FileMetadata, SpeakerStats
from .service import MetadataService

__all__ = [
    "AudioMetadataResult",
    "FileMetadata",
    "MetadataService",
    "SpeakerStats",
]
