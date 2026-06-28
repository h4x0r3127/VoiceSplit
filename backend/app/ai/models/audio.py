"""
Audio data models for the VoiceSplit AI pipeline.

Contains Pydantic v2 models representing raw and processed audio at various
stages of the pipeline — from initial upload metadata through to normalised
in-memory waveform data.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class UploadMetadata(BaseModel):
    """Metadata recorded at the time a file is uploaded to object storage.

    Populated by the upload endpoint and stored alongside the job record
    before any AI processing begins.
    """

    job_id: str = Field(..., description="Unique job identifier (UUID4).")
    original_filename: str = Field(..., description="Original filename as uploaded by the user.")
    s3_key: str = Field(..., description="Object storage key (MinIO / S3 path).")
    file_size_bytes: int = Field(..., ge=0, description="Raw file size in bytes.")
    content_type: str = Field(
        ..., description="MIME type of the uploaded file, e.g. 'audio/mpeg'."
    )
    uploaded_at: datetime = Field(..., description="UTC timestamp of the upload.")


class AudioMetadata(BaseModel):
    """Technical metadata describing an audio file's codec and signal properties.

    Populated by the preprocessing stage after the file has been probed with
    ffprobe / mutagen and before the waveform is decoded into memory.
    """

    duration_seconds: float = Field(
        ..., ge=0.0, description="Total duration of the audio file in seconds."
    )
    sample_rate: int = Field(
        ..., gt=0, description="Audio sample rate in Hz (e.g. 44100, 48000)."
    )
    channels: int = Field(..., ge=1, description="Number of audio channels (1=mono, 2=stereo).")
    bitrate_kbps: Optional[int] = Field(
        default=None, ge=0, description="Encoded bitrate in kbps; None for lossless formats."
    )
    format: str = Field(
        ..., description="Container / file format identifier: mp3, wav, flac, ogg, or aac."
    )
    codec: Optional[str] = Field(
        default=None, description="Audio codec identifier as reported by ffprobe, e.g. 'libmp3lame'."
    )
    bit_depth: Optional[int] = Field(
        default=None, ge=8, description="PCM bit depth (e.g. 16, 24, 32); None for lossy formats."
    )
    file_size_bytes: int = Field(..., ge=0, description="File size in bytes.")
    is_stereo: bool = Field(..., description="True when the file has exactly 2 channels.")
    has_multiple_speakers: Optional[bool] = Field(
        default=None,
        description=(
            "Whether the recording contains multiple speakers. "
            "Set to None before VAD runs; updated afterwards."
        ),
    )


class AudioData(BaseModel):
    """In-memory audio representation passed between pipeline stages.

    The ``waveform`` field holds a numpy ``ndarray`` of shape ``(samples,)``
    (mono, float32, 16 kHz) after preprocessing.  It is typed as ``Any`` to
    avoid a hard numpy import at module load time; the preprocessing stage is
    responsible for ensuring the correct dtype and shape.

    .. note::
        ``arbitrary_types_allowed`` is enabled so that numpy arrays can be
        stored without wrapping.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    waveform: Any = Field(
        ...,
        description=(
            "numpy ndarray of shape (samples,) — float32, mono, 16 000 Hz. "
            "Typed as Any to avoid a hard numpy import at module load time."
        ),
    )
    sample_rate: int = Field(..., gt=0, description="Sample rate of the waveform in Hz.")
    duration: float = Field(..., ge=0.0, description="Duration of the waveform in seconds.")
    file_path: str = Field(
        ...,
        description="Absolute local path to the temporary audio file on disk.",
    )
    metadata: Optional[AudioMetadata] = Field(
        default=None,
        description="Populated with codec metadata once the file has been probed.",
    )
