import uuid
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class SpeakerSegment(BaseModel):
    start: float
    end: float
    confidence: float


class SpeakerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_id: uuid.UUID
    label: str
    color: str
    gender: Optional[str] = None
    age_range: Optional[str] = None
    language: Optional[str] = None
    speaking_duration: float
    confidence: float
    emotion: Optional[str] = None
    accent: Optional[str] = None
    preview_s3_key: Optional[str] = None
    segments: Optional[List[SpeakerSegment]] = None
    created_at: datetime
    updated_at: datetime


class SpeakerUpdate(BaseModel):
    label: Optional[str] = None
    color: Optional[str] = None
