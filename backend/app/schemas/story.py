"""Pydantic schemas for Story validation, generation, and serialization."""

from datetime import datetime
from typing import Optional
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_validator,
    model_validator,
)

ALLOWED_GENRES: list[str] = [
    "Fantasy",
    "Adventure",
    "Mystery",
    "Comedy",
    "Romance",
    "Science Fiction",
    "Inspirational",
    "Fiction",
]

ALLOWED_MOODS: list[str] = [
    "Happy",
    "Emotional",
    "Mysterious",
    "Exciting",
    "Funny",
    "Peaceful",
    "Suspenseful",
]

ALLOWED_LENGTHS: list[str] = [
    "Short",
    "Medium",
    "Long",
]


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
        description="Genre of the story.",
        examples=["Fantasy"],
    )
    mood: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Atmosphere/mood of the story.",
        examples=["Mysterious"],
    )
    length: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Length classification (Short, Medium, Long).",
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
    """Schema for creating a new story directly."""
    pass


class GenerateStoryRequest(BaseModel):
    """Schema for initiating an AI story generation request."""

    prompt: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="User text prompt. Optional when an image is supplied.",
        examples=["A lost astronaut finds a living library on a distant comet."],
    )
    image_base64: Optional[str] = Field(
        default=None,
        description="Base64-encoded image string (JPEG, PNG, or WEBP, max 5 MB). Optional when prompt is supplied.",
    )
    genre: str = Field(
        ...,
        description=f"Selected genre. Allowed values: {', '.join(ALLOWED_GENRES)}",
        examples=["Science Fiction"],
    )
    mood: str = Field(
        ...,
        description=f"Selected mood. Allowed values: {', '.join(ALLOWED_MOODS)}",
        examples=["Mysterious"],
    )
    length: str = Field(
        ...,
        description=f"Selected story length. Allowed values: {', '.join(ALLOWED_LENGTHS)}",
        examples=["Short"],
    )

    @field_validator("genre")
    @classmethod
    def validate_genre(cls, value: str) -> str:
        trimmed = value.strip()
        for allowed in ALLOWED_GENRES:
            if trimmed.lower() == allowed.lower():
                return allowed
        raise ValueError(f"Invalid genre '{trimmed}'. Allowed: {', '.join(ALLOWED_GENRES)}")

    @field_validator("mood")
    @classmethod
    def validate_mood(cls, value: str) -> str:
        trimmed = value.strip()
        for allowed in ALLOWED_MOODS:
            if trimmed.lower() == allowed.lower():
                return allowed
        raise ValueError(f"Invalid mood '{trimmed}'. Allowed: {', '.join(ALLOWED_MOODS)}")

    @field_validator("length")
    @classmethod
    def validate_length(cls, value: str) -> str:
        trimmed = value.strip()
        for allowed in ALLOWED_LENGTHS:
            if trimmed.lower() == allowed.lower():
                return allowed
        raise ValueError(f"Invalid length '{trimmed}'. Allowed: {', '.join(ALLOWED_LENGTHS)}")

    @model_validator(mode="after")
    def validate_prompt_or_image_present(self) -> "GenerateStoryRequest":
        has_prompt = bool(self.prompt and self.prompt.strip())
        has_image = bool(self.image_base64 and self.image_base64.strip())

        if not has_prompt and not has_image:
            raise ValueError("At least one of text prompt or image must be supplied.")

        # Clean prompt if provided
        if self.prompt:
            self.prompt = self.prompt.strip()

        return self


class GeneratedStoryData(BaseModel):
    """Internal data transfer object for successfully generated stories."""

    title: str
    content: str
    prompt: Optional[str]
    image_filename: Optional[str]
    genre: str
    mood: str
    length: str
    word_count: int


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
