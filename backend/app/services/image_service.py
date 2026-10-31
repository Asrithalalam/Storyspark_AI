"""Image processing, validation, and storage service."""

import base64
import logging
import uuid
from pathlib import Path
from typing import Tuple

from app.config import settings

logger = logging.getLogger(__name__)


class ImageProcessingError(Exception):
    """Base exception for image processing issues."""
    pass


class ImageTooLargeError(ImageProcessingError):
    """Raised when an uploaded image exceeds size limits (HTTP 413)."""
    pass


class InvalidImageError(ImageProcessingError):
    """Raised when base64 payload is malformed or corrupted (HTTP 422)."""
    pass


class UnsupportedImageError(ImageProcessingError):
    """Raised when the image format is not permitted (HTTP 422)."""
    pass


def sniff_image_mime(data: bytes) -> Tuple[str, str] | None:
    """
    Inspect raw magic bytes to verify MIME type and canonical file extension.
    Supported types: PNG, JPEG, WEBP.
    """
    if len(data) < 12:
        return None

    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ("image/png", "png")

    if data.startswith(b"\xff\xd8\xff"):
        return ("image/jpeg", "jpg")

    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return ("image/webp", "webp")

    return None


def validate_and_decode_base64_image(image_base64: str) -> Tuple[bytes, str, str]:
    """
    Decode and validate a base64-encoded image string.

    Args:
        image_base64: Base64 string, optionally prefixed with data URI scheme.

    Returns:
        Tuple of (decoded_bytes, mime_type, file_extension).

    Raises:
        InvalidImageError: If the string is empty or invalid base64.
        ImageTooLargeError: If decoded image exceeds MAX_IMAGE_SIZE_BYTES (5 MB).
        UnsupportedImageError: If MIME type is not JPEG, PNG, or WEBP.
    """
    cleaned_input = image_base64.strip()
    if not cleaned_input:
        raise InvalidImageError("Image payload cannot be empty.")

    # Remove data URL scheme prefix if present (e.g. data:image/png;base64,...)
    if "," in cleaned_input and cleaned_input.startswith("data:"):
        _, payload = cleaned_input.split(",", 1)
        cleaned_input = payload.strip()

    try:
        image_bytes = base64.b64decode(cleaned_input, validate=True)
    except Exception as exc:
        logger.warning(f"Failed to decode base64 image: {exc}")
        raise InvalidImageError("Invalid base64 encoding for image data.") from None

    if not image_bytes:
        raise InvalidImageError("Decoded image content is empty.")

    # Enforce maximum image size (5 MB)
    if len(image_bytes) > settings.MAX_IMAGE_SIZE_BYTES:
        raise ImageTooLargeError(
            f"Image exceeds maximum allowable size of "
            f"{settings.MAX_IMAGE_SIZE_BYTES // (1024 * 1024)} MB."
        )

    # Inspect magic bytes to verify genuine MIME type
    sniffed = sniff_image_mime(image_bytes)
    if not sniffed or sniffed[0] not in settings.ALLOWED_IMAGE_MIME_TYPES:
        allowed_list = ", ".join(sorted(settings.ALLOWED_IMAGE_MIME_TYPES))
        raise UnsupportedImageError(
            f"Unsupported image format. Allowed formats: {allowed_list}."
        )

    mime_type, extension = sniffed
    return image_bytes, mime_type, extension


def save_image_to_uploads(image_bytes: bytes, extension: str) -> str:
    """
    Save validated image bytes to backend/data/uploads with a secure unique filename.

    Args:
        image_bytes: Raw decoded image bytes.
        extension: File extension without dot (e.g. 'png').

    Returns:
        Unique filename stored in data/uploads/.
    """
    settings.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.{extension}"
    target_path = settings.UPLOADS_DIR / filename

    with open(target_path, "wb") as f:
        f.write(image_bytes)

    logger.info(f"Saved uploaded image to {target_path} ({len(image_bytes)} bytes)")
    return filename


def cleanup_image_file(filename: str | None) -> None:
    """
    Safely delete an image file from the uploads directory (e.g. upon rollback).
    """
    if not filename:
        return
    try:
        # Prevent directory traversal attacks
        safe_name = Path(filename).name
        target_path = settings.UPLOADS_DIR / safe_name
        if target_path.exists() and target_path.is_file():
            target_path.unlink()
            logger.info(f"Cleaned up image file: {target_path}")
    except Exception as exc:
        logger.error(f"Failed to clean up image file '{filename}': {exc}")
