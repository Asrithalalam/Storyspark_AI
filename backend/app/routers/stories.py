"""API endpoints for Story persistent storage, retrieval, and AI generation."""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.story import (
    GenerateStoryRequest,
    StoryCreate,
    StoryDeleteResponse,
    StoryListItem,
    StoryResponse,
)
from app.services import ai_service, image_service, story_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stories", tags=["Stories"])


@router.post(
    "/generate",
    response_model=StoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate and persist a story using Gemma 4 AI",
    description="Processes creative preferences, generates a full narrative via Gemma 4, and saves it to SQLite.",
)
def generate_story_endpoint(
    req: GenerateStoryRequest,
    db: Session = Depends(get_db),
) -> StoryResponse:
    """
    Generate a story with the real Gemma 4 model and store it in SQLite.

    Accepts:
    - prompt (optional when image_base64 is present)
    - image_base64 (optional when prompt is present)
    - genre, mood, length (required creative parameters)
    """
    image_bytes = None
    mime_type = None
    image_filename = None

    # Step 1: Process and validate image if provided
    if req.image_base64:
        try:
            image_bytes, mime_type, extension = image_service.validate_and_decode_base64_image(
                req.image_base64
            )
            image_filename = image_service.save_image_to_uploads(image_bytes, extension)
        except image_service.ImageTooLargeError as exc:
            logger.warning(f"Image too large: {exc}")
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=str(exc),
            ) from None
        except (image_service.InvalidImageError, image_service.UnsupportedImageError) as exc:
            logger.warning(f"Image validation failed: {exc}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from None
        except Exception as exc:
            logger.error(f"Unexpected image processing error: {exc}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process the uploaded image.",
            ) from None

    # Step 2: Call the Gemma AI Generation Service
    try:
        title, content = ai_service.generate_story(
            prompt=req.prompt,
            image_bytes=image_bytes,
            mime_type=mime_type,
            genre=req.genre,
            mood=req.mood,
            length=req.length,
        )
    except ai_service.MissingApiKeyError as exc:
        image_service.cleanup_image_file(image_filename)
        logger.error(f"Configuration error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gemma API key is not configured on the server. Please set GEMINI_API_KEY in backend/.env.",
        ) from None
    except ai_service.InvalidApiKeyError as exc:
        image_service.cleanup_image_file(image_filename)
        logger.error(f"Authentication error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: Invalid Gemma API key.",
        ) from None
    except ai_service.QuotaExceededError as exc:
        image_service.cleanup_image_file(image_filename)
        logger.warning(f"Quota error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="AI generation quota or rate limit exceeded. Please try again later.",
        ) from None
    except ai_service.AiTimeoutError as exc:
        image_service.cleanup_image_file(image_filename)
        logger.error(f"Timeout error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="The AI model request timed out. Please try again.",
        ) from None
    except ai_service.EmptyResponseError as exc:
        image_service.cleanup_image_file(image_filename)
        logger.error(f"Empty response: {exc}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The AI model returned an empty story response. Please try again.",
        ) from None
    except ai_service.AiProviderError as exc:
        image_service.cleanup_image_file(image_filename)
        logger.error(f"AI Provider error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The AI service encountered an error while generating the story.",
        ) from None
    except Exception as exc:
        image_service.cleanup_image_file(image_filename)
        logger.error(f"Unexpected generation error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during story generation.",
        ) from None

    # Step 3: Verify narrative output
    if not title or not content:
        image_service.cleanup_image_file(image_filename)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Generated story was incomplete.",
        )

    # Step 4: Persist the story in SQLite
    story_in = StoryCreate(
        title=title,
        content=content,
        prompt=req.prompt,
        image_filename=image_filename,
        genre=req.genre,
        mood=req.mood,
        length=req.length,
    )

    try:
        story = story_service.create_story(db=db, story_in=story_in)
        logger.info(f"Successfully generated and persisted story '{title}' (ID: {story.id})")
        return StoryResponse.model_validate(story)
    except SQLAlchemyError as exc:
        image_service.cleanup_image_file(image_filename)
        logger.error(f"Database error saving generated story: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save the generated story to the database.",
        ) from None


@router.post(
    "",
    response_model=StoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a story manually",
    description="Directly persists a story to SQLite database storage for testing.",
)
def create_story_endpoint(
    story_in: StoryCreate,
    db: Session = Depends(get_db),
) -> StoryResponse:
    """Save a story directly to SQLite storage."""
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
        story = story_service.get_story_by_id(db=db, story_id=story_id)
        if not story:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Story with ID {story_id} was not found.",
            )

        # Clean up associated uploaded image file if present
        if story.image_filename:
            image_service.cleanup_image_file(story.image_filename)

        story_service.delete_story(db=db, story_id=story_id)
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.error(f"Error deleting story {story_id}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the story.",
        ) from None

    return StoryDeleteResponse(
        message="Story deleted successfully.",
        id=story_id,
    )
