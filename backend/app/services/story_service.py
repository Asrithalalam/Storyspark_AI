"""Database operations and business logic for Stories."""

import logging
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.story import Story
from app.schemas.story import StoryCreate

logger = logging.getLogger(__name__)


def create_story(db: Session, story_in: StoryCreate) -> Story:
    """
    Persist a new story to SQLite.

    Args:
        db: Active SQLAlchemy database session.
        story_in: Validated Story creation schema.

    Returns:
        The newly persisted Story with generated ID and timestamp.

    Raises:
        SQLAlchemyError: If the database operation fails.
    """
    story = Story(
        title=story_in.title,
        content=story_in.content,
        prompt=story_in.prompt,
        image_filename=story_in.image_filename,
        genre=story_in.genre,
        mood=story_in.mood,
        length=story_in.length,
    )
    try:
        db.add(story)
        db.commit()
        db.refresh(story)
        return story
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error(f"Failed to create story: {exc}")
        raise


def get_stories(db: Session, skip: int = 0, limit: int = 100) -> list[Story]:
    """
    Retrieve all stories, ordered newest first.

    Args:
        db: Active SQLAlchemy database session.
        skip: Pagination offset.
        limit: Maximum number of records to return.

    Returns:
        List of Story records ordered by created_at descending.
    """
    stmt = (
        select(Story)
        .order_by(Story.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


def get_story_by_id(db: Session, story_id: int) -> Story | None:
    """
    Retrieve a single story by its primary key ID.

    Args:
        db: Active SQLAlchemy database session.
        story_id: Integer primary key of the story.

    Returns:
        Story record if found, or None.
    """
    return db.get(Story, story_id)


def delete_story(db: Session, story_id: int) -> bool:
    """
    Delete a story by ID.

    Args:
        db: Active SQLAlchemy database session.
        story_id: Integer primary key of the story to delete.

    Returns:
        True if the story existed and was deleted; False if it was not found.

    Raises:
        SQLAlchemyError: If deletion fails.
    """
    story = db.get(Story, story_id)
    if not story:
        return False

    try:
        db.delete(story)
        db.commit()
        return True
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error(f"Failed to delete story {story_id}: {exc}")
        raise
