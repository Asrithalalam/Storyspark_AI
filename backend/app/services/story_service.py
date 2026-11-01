"""Database operations and business logic for Stories with user ownership scoping."""

import logging
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.story import Story
from app.schemas.story import StoryCreate

logger = logging.getLogger(__name__)


def create_story(db: Session, story_in: StoryCreate, user_id: int | None = None) -> Story:
    """
    Persist a new story to SQLite associated with an authenticated user.

    Args:
        db: Active SQLAlchemy database session.
        story_in: Validated Story creation schema.
        user_id: Optional integer ID of the owning user.

    Returns:
        The newly persisted Story with generated ID and timestamp.

    Raises:
        SQLAlchemyError: If the database operation fails.
    """
    owner_id = user_id if user_id is not None else story_in.user_id

    story = Story(
        title=story_in.title,
        content=story_in.content,
        prompt=story_in.prompt,
        image_filename=story_in.image_filename,
        genre=story_in.genre,
        mood=story_in.mood,
        length=story_in.length,
        user_id=owner_id,
    )
    try:
        db.add(story)
        db.commit()
        db.refresh(story)
        logger.info(f"Persisted story '{story.title}' (ID: {story.id}, user_id: {story.user_id})")
        return story
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error(f"Failed to create story: {exc}")
        raise


def get_stories(db: Session, user_id: int | None = None, skip: int = 0, limit: int = 100) -> list[Story]:
    """
    Retrieve stories owned by a specific user, ordered newest first.
    Legacy stories with user_id=None are excluded when user_id is specified.

    Args:
        db: Active SQLAlchemy database session.
        user_id: Required user ID to scope queries to the owner.
        skip: Pagination offset.
        limit: Maximum number of records to return.

    Returns:
        List of Story records owned by user_id ordered by created_at descending.
    """
    stmt = select(Story).order_by(Story.created_at.desc()).offset(skip).limit(limit)
    if user_id is not None:
        stmt = stmt.where(Story.user_id == user_id)
    else:
        stmt = stmt.where(Story.user_id.is_(None))

    return list(db.scalars(stmt).all())


def get_story_by_id(db: Session, story_id: int, user_id: int | None = None) -> Story | None:
    """
    Retrieve a single story by primary key ID scoped to its owner.
    Returns None if the story does not exist or belongs to another user.

    Args:
        db: Active SQLAlchemy database session.
        story_id: Integer primary key of the story.
        user_id: Optional integer ID of the owning user for authorization.

    Returns:
        Story record if found and authorized, or None.
    """
    if user_id is not None:
        stmt = select(Story).where(Story.id == story_id, Story.user_id == user_id)
        return db.scalars(stmt).first()
    return db.get(Story, story_id)


def delete_story(db: Session, story_id: int, user_id: int | None = None) -> bool:
    """
    Delete a story by ID scoped to its owner.

    Args:
        db: Active SQLAlchemy database session.
        story_id: Integer primary key of the story to delete.
        user_id: Optional integer ID of the owning user for authorization.

    Returns:
        True if the story existed, belonged to the user, and was deleted; False otherwise.

    Raises:
        SQLAlchemyError: If deletion fails.
    """
    story = get_story_by_id(db=db, story_id=story_id, user_id=user_id)
    if not story:
        return False

    try:
        db.delete(story)
        db.commit()
        logger.info(f"Deleted story ID {story_id} for user_id: {user_id}")
        return True
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error(f"Failed to delete story {story_id}: {exc}")
        raise


def bulk_delete_stories(
    db: Session,
    story_ids: list[int],
    user_id: int | None = None,
) -> tuple[int, list[int], list[str]]:
    """
    Transactionally delete multiple stories owned by the authorized user.

    Args:
        db: Active SQLAlchemy database session.
        story_ids: List of integer story IDs to delete.
        user_id: Optional integer ID of the owning user.

    Returns:
        Tuple of (deleted_count, deleted_ids, image_filenames_to_clean).

    Raises:
        SQLAlchemyError: If the transaction fails.
    """
    if not story_ids:
        return 0, [], []

    try:
        stmt = select(Story).where(Story.id.in_(story_ids))
        if user_id is not None:
            stmt = stmt.where(Story.user_id == user_id)

        stories = list(db.scalars(stmt).all())

        if not stories:
            return 0, [], []

        deleted_ids = [s.id for s in stories]
        image_filenames = [s.image_filename for s in stories if s.image_filename]

        for s in stories:
            db.delete(s)

        db.commit()
        logger.info(f"Bulk deleted {len(deleted_ids)} stories for user_id {user_id}: {deleted_ids}")
        return len(deleted_ids), deleted_ids, image_filenames
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error(f"Failed bulk deletion for IDs {story_ids}: {exc}")
        raise


def clear_all_stories(db: Session, user_id: int | None = None) -> tuple[int, list[str]]:
    """
    Transactionally delete all stories belonging to the authenticated user.
    Legacy stories (user_id=None) are never deleted when user_id is provided.

    Args:
        db: Active SQLAlchemy database session.
        user_id: Optional integer ID of the owning user.

    Returns:
        Tuple of (deleted_count, image_filenames_to_clean).

    Raises:
        SQLAlchemyError: If the transaction fails.
    """
    try:
        stmt = select(Story)
        if user_id is not None:
            stmt = stmt.where(Story.user_id == user_id)
        else:
            stmt = stmt.where(Story.user_id.is_(None))

        stories = list(db.scalars(stmt).all())

        if not stories:
            return 0, []

        image_filenames = [s.image_filename for s in stories if s.image_filename]
        count = len(stories)

        for s in stories:
            db.delete(s)

        db.commit()
        logger.info(f"Cleared all {count} stories for user_id: {user_id}")
        return count, image_filenames
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error(f"Failed to clear stories for user_id {user_id}: {exc}")
        raise
