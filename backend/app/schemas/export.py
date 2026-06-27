import uuid
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict

from app.models.export import ExportFormat, ExportStatus


class ExportCreate(BaseModel):
    job_id: uuid.UUID
    selected_speaker_ids: List[uuid.UUID]
    output_format: ExportFormat


class ExportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_id: uuid.UUID
    status: ExportStatus
    output_format: ExportFormat
    download_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
