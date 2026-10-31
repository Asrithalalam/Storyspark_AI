"""Database configuration and session management for StorySpark AI."""

from datetime import datetime, timezone
from typing import Generator
from sqlalchemy import DateTime, TypeDecorator, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class UTCDateTime(TypeDecorator):
    """
    Ensures DateTime values are always stored and retrieved as timezone-aware UTC datetimes.
    SQLite stores datetimes without timezone info by default.
    """

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect) -> datetime | None:
        if value is not None:
            if not isinstance(value, datetime):
                raise TypeError("Expected datetime object")
            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc)
        return value

    def process_result_value(self, value: datetime | None, dialect) -> datetime | None:
        if value is not None:
            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc)
        return value


class Base(DeclarativeBase):
    """SQLAlchemy 2.x declarative base class."""
    pass


# SQLite connection configuration
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency yielding a SQLAlchemy session.
    Guarantees the session is properly closed after each request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
