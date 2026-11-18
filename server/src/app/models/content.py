import enum
from datetime import datetime

from sqlalchemy import Text, DateTime, Enum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ContentType(str, enum.Enum):
    TEXT = "text"
    URL = "url"


class ContentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    FAILED = "failed"
    READY = "ready"


class Content(Base):
    __tablename__ = "contents"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    title: Mapped[str] = mapped_column(String, nullable=True)

    source: Mapped[str] = mapped_column(String, nullable=True)

    content: Mapped[str] = mapped_column(Text, nullable=False)

    type: Mapped[ContentType] = mapped_column(
        Enum(ContentType), nullable=False
    )

    status: Mapped[ContentStatus] = mapped_column(
        Enum(ContentStatus),
        default=ContentStatus.PENDING,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    embeddings = relationship("Embedding", back_populates="content", cascade="all, delete-orphan")