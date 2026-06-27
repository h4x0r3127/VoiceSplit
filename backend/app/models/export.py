import uuid
import enum
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.job import Job
    from app.models.user import User


class ExportStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ExportFormat(str, enum.Enum):
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    TXT = "txt"
    JSON = "json"
    CSV = "csv"


class Export(TimestampMixin, Base):
    __tablename__ = "exports"

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    selected_speaker_ids: Mapped[List[str]] = mapped_column(JSONB, nullable=False, default=list)
    output_format: Mapped[ExportFormat] = mapped_column(
        SAEnum(ExportFormat, name="export_format"),
        nullable=False,
    )
    output_s3_key: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    status: Mapped[ExportStatus] = mapped_column(
        SAEnum(ExportStatus, name="export_status"),
        nullable=False,
        default=ExportStatus.PENDING,
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    job: Mapped["Job"] = relationship("Job", lazy="select")
    user: Mapped["User"] = relationship("User", back_populates="exports")
