import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    name: str
    avatar_url: Optional[str] = None
    credits: int
    storage_used_bytes: int
    is_verified: bool
    created_at: datetime


class UserUpdate(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserAnalytics(BaseModel):
    total_jobs: int
    completed_jobs: int
    total_minutes_processed: float
    total_speakers_found: int
    storage_used_bytes: int
