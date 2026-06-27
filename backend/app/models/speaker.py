import uuid
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.job import Job


class Speaker(TimestampMixin, Base):
    __tablename__ = "speakers"

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    label: Mapped[str] = mapped_column(String(128), nullable=False)
    color: Mapped[str] = mapped_column(String(16), nullable=False, default="#06D6CF")
    gender: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    age_range: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    speaking_duration: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    emotion: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    accent: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    preview_s3_key: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    embedding: Mapped[Optional[List[float]]] = mapped_column(JSONB, nullable=True)
    segments: Mapped[Optional[List[dict]]] = mapped_column(JSONB, nullable=True)

    job: Mapped["Job"] = relationship("Job", back_populates="speakers")
