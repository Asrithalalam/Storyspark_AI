"""Pydantic schemas for Story validation and serialization."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator


class StoryBase(BaseModel):
    """Base story attributes with validation constraints."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Story title (1-255 characters).",
        examples=["The Clockwork Dragon"],
    )
    content: str = Field(
        ...,
        min_length=1,
        description="Complete story narrative text.",
        examples=["In the heart of the brass forest, tick-tock echoed through the trees..."],
    )
    prompt: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Original text prompt; nullable for image-only creations.",
        examples=["A fantasy story about a mechanical dragon in a clockwork forest."],
    )
    image_filename: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Uploaded image filename reference for future visual story support.",
        examples=["clockwork_dragon.png"],
    )
    genre: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Genre of the story (e.g. Fantasy, Sci-Fi, Mystery).",
        examples=["Fantasy"],
    )
    mood: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Atmosphere/mood of the story (e.g. Whimsical, Dark, Inspiring).",
        examples=["Whimsical"],
    )
    length: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Length classification (e.g. Short, Medium, Long).",
        examples=["Short"],
    )

    @field_validator("title", "genre", "mood", "length")
    @classmethod
    def validate_non_empty_strings(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Field cannot be empty or contain only whitespace.")
        return trimmed

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Story content cannot be empty.")
        return trimmed


class StoryCreate(StoryBase):
    """Schema for creating a new story."""
    pass


class StoryResponse(StoryBase):
    """Schema for returning full story details."""

    id: int = Field(..., description="Unique story identifier.")
    created_at: datetime = Field(..., description="UTC creation timestamp.")

    model_config = ConfigDict(from_attributes=True)


class StoryListItem(BaseModel):
    """Schema for story summary listing, designed for the history sidebar."""

    id: int = Field(..., description="Unique story identifier.")
    title: str = Field(..., description="Story title.")
    prompt: Optional[str] = Field(None, description="Original prompt.")
    image_filename: Optional[str] = Field(None, description="Image filename reference.")
    genre: str = Field(..., description="Story genre.")
    mood: str = Field(..., description="Story mood.")
    length: str = Field(..., description="Story length.")
    content: str = Field(..., description="Full story content.")
    created_at: datetime = Field(..., description="UTC creation timestamp.")

    @computed_field
    @property
    def content_preview(self) -> str:
        """Snippet of content for preview cards or sidebar lists."""
        cleaned = " ".join(self.content.split())
        if len(cleaned) <= 120:
            return cleaned
        return f"{cleaned[:117]}..."

    model_config = ConfigDict(from_attributes=True)


class StoryDeleteResponse(BaseModel):
    """Schema returned after successfully deleting a story."""

    message: str = Field(..., description="Deletion confirmation message.")
    id: int = Field(..., description="Identifier of the deleted story.")
