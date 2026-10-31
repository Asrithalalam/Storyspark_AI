"""SQLAlchemy model for persistent Story storage."""

from datetime import datetime, timezone
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, UTCDateTime


class Story(Base):
    """
    Persistent Story entity in SQLite.
    Stores generated/saved stories with metadata and timestamps.
    """

    __tablename__ = "stories"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
        doc="Unique primary key identifier for the story.",
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Story title.",
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Complete body text of the story.",
    )
    prompt: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        default=None,
        doc="Original text prompt; nullable for image-only creations.",
    )
    image_filename: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        default=None,
        doc="Uploaded image filename reference for future visual story support.",
    )
    genre: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="Selected genre (e.g. Fantasy, Sci-Fi, Mystery).",
    )
    mood: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="Selected mood (e.g. Whimsical, Dark, Inspiring).",
    )
    length: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="Selected length option (e.g. Short, Medium, Long).",
    )
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
        doc="Timezone-aware UTC timestamp when the story was created.",
    )

    def __repr__(self) -> str:
        return f"<Story(id={self.id}, title='{self.title}', genre='{self.genre}')>"
