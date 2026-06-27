import uuid
import enum
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Boolean, BigInteger, Integer, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.job import Job
    from app.models.export import Export


class AuthProvider(str, enum.Enum):
    EMAIL = "email"
    GOOGLE = "google"


class User(TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    provider: Mapped[AuthProvider] = mapped_column(
        SAEnum(AuthProvider, name="auth_provider"),
        nullable=False,
        default=AuthProvider.EMAIL,
    )
    provider_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    credits: Mapped[int] = mapped_column(Integer, nullable=False, default=300)
    storage_used_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    jobs: Mapped[List["Job"]] = relationship("Job", back_populates="user", lazy="select")
    exports: Mapped[List["Export"]] = relationship("Export", back_populates="user", lazy="select")
