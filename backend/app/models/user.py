"""SQLAlchemy model for persistent User entity and authentication."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, UTCDateTime

if TYPE_CHECKING:
    from app.models.story import Story


class User(Base):
    """
    Persistent User entity in SQLite.
    Stores account credentials, profile details, authentication provider info,
    and timestamps.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
        doc="Unique primary key identifier for the user.",
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        doc="Unique user email address (stored in normalized lowercase).",
    )
    hashed_password: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        default=None,
        doc="Cryptographic password hash. Nullable for Google OAuth accounts.",
    )
    full_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        default=None,
        doc="User's full display name.",
    )
    avatar_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        default=None,
        doc="User avatar or Google profile photo URL.",
    )
    auth_provider: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="local",
        doc="Authentication provider: 'local' (email/password) or 'google'.",
    )
    google_sub: Mapped[str | None] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=True,
        default=None,
        doc="Google Subject ID from verified ID token for OAuth users.",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Flag indicating whether the account is currently active.",
    )
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
        doc="Timezone-aware UTC timestamp when the user registered.",
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Timezone-aware UTC timestamp when the account profile was last updated.",
    )

    # 1-to-many relationship: A user can own multiple stories
    stories: Mapped[list["Story"]] = relationship(
        "Story",
        back_populates="owner",
        cascade="all, delete-orphan",
        doc="Stories authored by this user.",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', auth_provider='{self.auth_provider}')>"
