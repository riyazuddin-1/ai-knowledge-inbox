from sqlalchemy import Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.database.sql import Base

class Embedding(Base):
    __tablename__ = "embeddings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    content_id: Mapped[int] = mapped_column(Integer, ForeignKey("contents.id", ondelete="CASCADE"), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0) # chunk order

    text: Mapped[str] = mapped_column(Text, nullable=False) # chunk content
    embedding: Mapped[str] = mapped_column(Text, nullable=False) # Stored as JSON string of floats

    content = relationship("Content", back_populates="embeddings")