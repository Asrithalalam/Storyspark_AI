"""Database configuration, session management, and migrations for StorySpark AI."""

from datetime import datetime, timezone
import logging
from typing import Generator
from sqlalchemy import DateTime, TypeDecorator, create_engine, event, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

logger = logging.getLogger(__name__)


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

# Enable SQLite foreign key constraint enforcement
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if settings.DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


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


def run_migrations(target_engine=None) -> None:
    """
    Perform safe, non-destructive schema migrations for existing databases.
    Preserves all existing data.
    """
    eng = target_engine or engine
    inspector = inspect(eng)
    table_names = inspector.get_table_names()

    if "stories" in table_names:
        columns = [col["name"] for col in inspector.get_columns("stories")]
        if "user_id" not in columns:
            logger.info("Migrating 'stories' table: Adding 'user_id' foreign key column...")
            with eng.begin() as conn:
                conn.execute(
                    text("ALTER TABLE stories ADD COLUMN user_id INTEGER REFERENCES users(id)")
                )
                conn.execute(
                    text("CREATE INDEX IF NOT EXISTS ix_stories_user_id ON stories (user_id)")
                )
            logger.info("Successfully added 'user_id' column and index to 'stories' table.")


def init_db() -> None:
    """
    Initialize database tables and run pending schema migrations.
    Guarantees all models (User, Story) are registered before create_all.
    """
    import app.models  # noqa: F401 - ensures all models are registered in Base.metadata

    # 1. Create any missing tables (e.g. 'users' if it does not exist)
    Base.metadata.create_all(bind=engine)

    # 2. Run non-destructive column migrations (e.g. add user_id to existing stories table)
    run_migrations(engine)
