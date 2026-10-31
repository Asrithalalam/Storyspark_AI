"""API endpoints for Story persistent storage and retrieval."""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.story import (
    StoryCreate,
    StoryDeleteResponse,
    StoryListItem,
    StoryResponse,
)
from app.services import story_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stories", tags=["Stories"])


@router.post(
    "",
    response_model=StoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new story",
    description="Validates and persists a story to SQLite database storage.",
)
def create_story_endpoint(
    story_in: StoryCreate,
    db: Session = Depends(get_db),
) -> StoryResponse:
    """Save a new story to SQLite storage."""
    try:
        story = story_service.create_story(db=db, story_in=story_in)
        return StoryResponse.model_validate(story)
    except SQLAlchemyError as exc:
        logger.error(f"Error persisting story: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store the story in the database. Please try again.",
        ) from None


@router.get(
    "",
    response_model=List[StoryListItem],
    status_code=status.HTTP_200_OK,
    summary="List all stories",
    description="Retrieve saved stories ordered newest first for history views.",
)
def list_stories_endpoint(
    skip: int = Query(0, ge=0, description="Number of stories to skip"),
    limit: int = Query(100, ge=1, le=200, description="Maximum stories to return"),
    db: Session = Depends(get_db),
) -> List[StoryListItem]:
    """Retrieve all stories ordered by creation time descending."""
    try:
        stories = story_service.get_stories(db=db, skip=skip, limit=limit)
        return [StoryListItem.model_validate(s) for s in stories]
    except SQLAlchemyError as exc:
        logger.error(f"Error listing stories: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve stories from the database.",
        ) from None


@router.get(
    "/{story_id}",
    response_model=StoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve a single story",
    description="Retrieve the complete details of a specific story by its unique ID.",
)
def get_story_endpoint(
    story_id: int,
    db: Session = Depends(get_db),
) -> StoryResponse:
    """Retrieve a single story by ID. Returns 404 if not found."""
    try:
        story = story_service.get_story_by_id(db=db, story_id=story_id)
    except SQLAlchemyError as exc:
        logger.error(f"Error retrieving story {story_id}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while accessing the database.",
        ) from None

    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Story with ID {story_id} was not found.",
        )

    return StoryResponse.model_validate(story)


@router.delete(
    "/{story_id}",
    response_model=StoryDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a story",
    description="Permanently delete a story from SQLite database storage.",
)
def delete_story_endpoint(
    story_id: int,
    db: Session = Depends(get_db),
) -> StoryDeleteResponse:
    """Delete a story by ID. Returns 404 if not found."""
    try:
        deleted = story_service.delete_story(db=db, story_id=story_id)
    except SQLAlchemyError as exc:
        logger.error(f"Error deleting story {story_id}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the story.",
        ) from None

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Story with ID {story_id} was not found.",
        )

    return StoryDeleteResponse(
        message="Story deleted successfully.",
        id=story_id,
    )
