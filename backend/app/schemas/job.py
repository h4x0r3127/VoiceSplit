import uuid
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict

from app.models.job import JobStatus


class SpeakerSegmentBrief(BaseModel):
    start: float
    end: float
    confidence: float


class SpeakerBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    label: str
    color: str
    gender: Optional[str] = None
    language: Optional[str] = None
    speaking_duration: float
    confidence: float
    emotion: Optional[str] = None
    preview_s3_key: Optional[str] = None
    segments: Optional[List[SpeakerSegmentBrief]] = None


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    original_filename: str
    original_s3_key: str
    processed_s3_key: Optional[str] = None
    status: JobStatus
    pipeline_stage: Optional[str] = None
    progress: int
    duration_seconds: Optional[float] = None
    file_size_bytes: int
    error_message: Optional[str] = None
    audio_metadata: Optional[dict] = None
    speakers: List[SpeakerBrief] = []
    created_at: datetime
    updated_at: datetime


class JobListResponse(BaseModel):
    items: List[JobResponse]
    total: int
    page: int
    per_page: int


class JobProgressUpdate(BaseModel):
    job_id: str
    status: str
    stage: str
    progress: int
    message: str
    error: Optional[str] = None


class JobStatusResponse(BaseModel):
    """Lightweight response for the polling /jobs/{id}/status endpoint."""

    job_id: str
    status: JobStatus
    pipeline_stage: Optional[str] = None
    progress: int
    error_message: Optional[str] = None
    duration_seconds: Optional[float] = None
    audio_metadata: Optional[dict] = None

