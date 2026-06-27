import uuid
import enum
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Integer, BigInteger, Float, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.speaker import Speaker


class JobStatus(str, enum.Enum):
    UPLOADED = "UPLOADED"
    PREPROCESSING = "PREPROCESSING"
    VAD = "VAD"
    DIARIZING = "DIARIZING"
    EMBEDDING = "EMBEDDING"
    CLUSTERING = "CLUSTERING"
    SEPARATING = "SEPARATING"
    TRANSCRIBING = "TRANSCRIBING"
    ANALYZING = "ANALYZING"
    RECONSTRUCTING = "RECONSTRUCTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Job(TimestampMixin, Base):
    __tablename__ = "jobs"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    original_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    original_s3_key: Mapped[str] = mapped_column(String(1024), nullable=False)
    processed_s3_key: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    status: Mapped[JobStatus] = mapped_column(
        SAEnum(JobStatus, name="job_status"),
        nullable=False,
        default=JobStatus.UPLOADED,
        index=True,
    )
    pipeline_stage: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    audio_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="jobs")
    speakers: Mapped[List["Speaker"]] = relationship(
        "Speaker", back_populates="job", cascade="all, delete-orphan", lazy="select"
    )
