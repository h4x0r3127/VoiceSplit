"""Audio metadata extraction utilities using mutagen (pure Python, no ffprobe required).

Supports: MP3, WAV, FLAC, AAC/M4A, OGG, and generic fallback.
Returns a canonical AudioMetadata dict that maps to the Job.audio_metadata JSONB column.
"""
from __future__ import annotations

import os
import mimetypes
from typing import Optional
from dataclasses import dataclass, asdict

from app.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class AudioMetadata:
    """Canonical metadata extracted from an audio file."""

    duration_seconds: float
    sample_rate: Optional[int]
    channels: Optional[int]
    bitrate_kbps: Optional[int]
    format: str          # e.g. "mp3", "wav", "flac"
    codec: Optional[str]
    file_size_bytes: int
    title: Optional[str] = None
    artist: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


def extract_audio_metadata(file_path: str) -> AudioMetadata:
    """
    Extract audio metadata from a file on disk.
    Falls back gracefully when format-specific parsers aren't available.

    Args:
        file_path: Absolute path to the audio file on disk.

    Returns:
        AudioMetadata populated with whatever can be determined.

    Raises:
        ValueError: If the file cannot be read or is not a recognisable audio format.
    """
    import mutagen

    file_size = os.path.getsize(file_path)
    ext = os.path.splitext(file_path)[-1].lower().lstrip(".")

    try:
        audio = mutagen.File(file_path, easy=True)
    except Exception as exc:
        logger.error("mutagen_failed", path=file_path, error=str(exc))
        raise ValueError(f"Cannot parse audio file '{file_path}': {exc}") from exc

    if audio is None:
        raise ValueError(f"Unrecognised audio format for file '{file_path}'")

    # --- Duration ---
    duration: float = getattr(audio.info, "length", 0.0) or 0.0

    # --- Sample rate ---
    sample_rate: Optional[int] = getattr(audio.info, "sample_rate", None)

    # --- Channels ---
    channels: Optional[int] = getattr(audio.info, "channels", None)

    # --- Bitrate ---
    raw_bitrate = getattr(audio.info, "bitrate", None)
    bitrate_kbps: Optional[int] = int(raw_bitrate / 1000) if raw_bitrate else None

    # --- Format ---
    type_name = type(audio).__module__.split(".")[-1]
    fmt = _normalise_format(ext or type_name)

    # --- Codec ---
    codec: Optional[str] = _get_codec(audio)

    # --- Tags ---
    title: Optional[str] = _tag(audio, "title")
    artist: Optional[str] = _tag(audio, "artist")

    metadata = AudioMetadata(
        duration_seconds=round(duration, 3),
        sample_rate=sample_rate,
        channels=channels,
        bitrate_kbps=bitrate_kbps,
        format=fmt,
        codec=codec,
        file_size_bytes=file_size,
        title=title,
        artist=artist,
    )

    logger.info(
        "audio_metadata_extracted",
        path=file_path,
        duration=metadata.duration_seconds,
        format=fmt,
        sample_rate=sample_rate,
    )
    return metadata


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalise_format(raw: str) -> str:
    mapping = {
        "mp3": "mp3",
        "mp4": "m4a",
        "m4a": "m4a",
        "aac": "aac",
        "flac": "flac",
        "wav": "wav",
        "ogg": "ogg",
        "wave": "wav",
    }
    return mapping.get(raw.lower(), raw.lower())


def _get_codec(audio) -> Optional[str]:
    """Best-effort codec detection from mutagen audio object."""
    info = getattr(audio, "info", None)
    if info is None:
        return None
    # MP3
    if hasattr(info, "mode"):
        return "mp3"
    # FLAC
    if hasattr(info, "bits_per_sample"):
        return "flac" if info.bits_per_sample else None
    # OGG Vorbis / Opus
    codec_attr = getattr(info, "_type", None) or getattr(info, "codec", None)
    if codec_attr:
        return str(codec_attr).lower()
    return None


def _tag(audio, key: str) -> Optional[str]:
    """Safely extract a tag value from a mutagen EasyID3-style dict."""
    try:
        values = audio.get(key)
        if values and isinstance(values, list):
            return str(values[0])
        if values:
            return str(values)
    except Exception:
        pass
    return None
