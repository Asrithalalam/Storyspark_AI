"""Unit tests for Stage 1 Authentication Database Models and Migrations."""

from datetime import datetime, timezone
import pytest
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app.database import Base, run_migrations
from app.models.story import Story
from app.models.user import User


def test_user_table_schema(db_session: Session):
    """Verify the 'users' table schema, columns, and constraints."""
    engine = db_session.get_bind()
    inspector = inspect(engine)

    assert "users" in inspector.get_table_names()

    columns = {col["name"]: col for col in inspector.get_columns("users")}
    expected_cols = [
        "id",
        "email",
        "hashed_password",
        "full_name",
        "avatar_url",
        "auth_provider",
        "google_sub",
        "is_active",
        "created_at",
        "updated_at",
    ]

    for col_name in expected_cols:
        assert col_name in columns, f"Column '{col_name}' must exist in 'users' table"

    # Verify email is not nullable
    assert columns["email"]["nullable"] is False

    # Verify hashed_password is nullable for Google OAuth users
    assert columns["hashed_password"]["nullable"] is True


def test_story_table_has_user_id_column(db_session: Session):
    """Verify the 'stories' table has the user_id foreign key column."""
    engine = db_session.get_bind()
    inspector = inspect(engine)

    columns = {col["name"]: col for col in inspector.get_columns("stories")}
    assert "user_id" in columns
    assert columns["user_id"]["nullable"] is True


def test_create_user_and_associate_story(db_session: Session):
    """Verify creating a user, creating an associated story, and relationship navigation."""
    user = User(
        email="storyteller@storyspark.ai",
        hashed_password="secure_hash_placeholder",
        full_name="Story Teller",
        auth_provider="local",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    assert user.email == "storyteller@storyspark.ai"
    assert user.created_at is not None

    # Create a story belonging to this user
    story = Story(
        title="The Luminescent Grove",
        content="Glowworms illuminated the hollow of the elder tree.",
        prompt="A grove illuminated by mystical glowworms.",
        genre="Fantasy",
        mood="Whimsical",
        length="Short",
        user_id=user.id,
    )
    db_session.add(story)
    db_session.commit()
    db_session.refresh(story)

    assert story.id is not None
    assert story.user_id == user.id
    assert story.owner is not None
    assert story.owner.email == "storyteller@storyspark.ai"

    # Check reverse relationship
    db_session.refresh(user)
    assert len(user.stories) == 1
    assert user.stories[0].title == "The Luminescent Grove"


def test_legacy_story_with_null_user_id_is_valid(db_session: Session):
    """Verify legacy stories with user_id=None are preserved and valid."""
    legacy_story = Story(
        title="Ancient Chronicle",
        content="A tale whispered long before account registrations.",
        prompt="A story from an anonymous author.",
        genre="Mystery",
        mood="Mysterious",
        length="Short",
        user_id=None,
    )
    db_session.add(legacy_story)
    db_session.commit()
    db_session.refresh(legacy_story)

    assert legacy_story.id is not None
    assert legacy_story.user_id is None
    assert legacy_story.owner is None


def test_cascade_delete_user_deletes_owned_stories(db_session: Session):
    """Verify that deleting a user cascades to delete their authored stories."""
    user = User(
        email="temp_author@storyspark.ai",
        hashed_password="hash",
        full_name="Temporary Author",
        auth_provider="local",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    story = Story(
        title="Ephemeral Tale",
        content="This tale will be removed when its author departs.",
        prompt="A story with an ephemeral author.",
        genre="Fiction",
        mood="Emotional",
        length="Short",
        user_id=user.id,
    )
    db_session.add(story)
    db_session.commit()
    story_id = story.id

    # Delete the user
    db_session.delete(user)
    db_session.commit()

    # Verify story was deleted
    deleted_story = db_session.get(Story, story_id)
    assert deleted_story is None


def test_migration_is_idempotent(db_session: Session):
    """Verify running migrations multiple times causes no errors or duplicate columns."""
    engine = db_session.get_bind()
    # Running run_migrations again should be a safe no-op
    run_migrations(engine)
    run_migrations(engine)
    inspector = inspect(engine)
    columns = [col["name"] for col in inspector.get_columns("stories")]
    assert columns.count("user_id") == 1
