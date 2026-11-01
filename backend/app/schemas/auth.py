"""Pydantic schemas for authentication requests, responses, and user profiles."""

from datetime import datetime
import re
from pydantic import BaseModel, ConfigDict, Field, field_validator


EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class RegisterRequest(BaseModel):
    """Payload for email and password user registration."""

    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="User password (minimum 8 characters)")
    full_name: str | None = Field(default=None, max_length=100, description="Optional full display name")

    @field_validator("email")
    @classmethod
    def validate_and_normalize_email(cls, v: str) -> str:
        v_clean = v.strip().lower()
        if not v_clean or not EMAIL_REGEX.match(v_clean) or len(v_clean) > 255:
            raise ValueError("Invalid email address format.")
        return v_clean

    @field_validator("full_name")
    @classmethod
    def clean_full_name(cls, v: str | None) -> str | None:
        if v is None:
            return None
        cleaned = v.strip()
        return cleaned if cleaned else None


class LoginRequest(BaseModel):
    """Payload for local email and password authentication."""

    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=1, max_length=128, description="User password")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class UserResponse(BaseModel):
    """Safe user profile response omitting credentials and private tokens."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str | None = None
    avatar_url: str | None = None
    auth_provider: str
    created_at: datetime


class MessageResponse(BaseModel):
    """Generic status and message response."""

    message: str
