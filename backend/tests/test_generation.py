"""Unit tests for Phase 4 Gemma AI Story Generation and Image handling."""

import base64
from unittest.mock import MagicMock, patch
import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.schemas.story import GenerateStoryRequest
from app.services import ai_service, image_service

TINY_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
    b"\x00\x00\x00\rIDATx\x9cc\xf8\xff\xff?\x03\x00\x08\xfc\x02\xfe\xa7\x9a\xa0\xa0\x00\x00\x00\x00IEND\xaeB`\x82"
)
VALID_B64_PNG = base64.b64encode(TINY_PNG_BYTES).decode("utf-8")


# ---------------------------------------------------------------------------
# 1. Request Validation Tests
# ---------------------------------------------------------------------------
def test_validation_missing_prompt_and_image(client: TestClient):
    """At least one of prompt or image must be provided."""
    res = client.post("/api/stories/generate", json={
        "genre": "Fantasy",
        "mood": "Mysterious",
        "length": "Short",
    })
    assert res.status_code == 422
    assert "at least one of text prompt or image" in res.text.lower()


def test_validation_whitespace_only_prompt_and_no_image(client: TestClient):
    """Whitespace-only prompt with no image should be rejected."""
    res = client.post("/api/stories/generate", json={
        "prompt": "   ",
        "genre": "Fantasy",
        "mood": "Mysterious",
        "length": "Short",
    })
    assert res.status_code == 422
    assert "at least one of text prompt or image" in res.text.lower()


def test_validation_invalid_genre(client: TestClient):
    """Unsupported genre must be rejected with 422."""
    res = client.post("/api/stories/generate", json={
        "prompt": "Valid creative prompt",
        "genre": "CyberpunkCooking",
        "mood": "Mysterious",
        "length": "Short",
    })
    assert res.status_code == 422
    assert "invalid genre" in res.text.lower()


def test_validation_invalid_mood(client: TestClient):
    """Unsupported mood must be rejected with 422."""
    res = client.post("/api/stories/generate", json={
        "prompt": "Valid creative prompt",
        "genre": "Fantasy",
        "mood": "Bored",
        "length": "Short",
    })
    assert res.status_code == 422
    assert "invalid mood" in res.text.lower()


def test_validation_invalid_length(client: TestClient):
    """Unsupported length must be rejected with 422."""
    res = client.post("/api/stories/generate", json={
        "prompt": "Valid creative prompt",
        "genre": "Fantasy",
        "mood": "Mysterious",
        "length": "ExtraExtraLong",
    })
    assert res.status_code == 422
    assert "invalid length" in res.text.lower()


# ---------------------------------------------------------------------------
# 2. Response Parsing Tests
# ---------------------------------------------------------------------------
def test_parse_story_response_standard():
    raw = "TITLE: The Whispering Forest\nCONTENT:\nDeep in the misty woods, ancient trees talked."
    title, content = ai_service.parse_story_response(raw)
    assert title == "The Whispering Forest"
    assert content == "Deep in the misty woods, ancient trees talked."


def test_parse_story_response_markdown():
    raw = "# The Brass Compass\n\nA brass compass spun wildly beneath the aurora."
    title, content = ai_service.parse_story_response(raw)
    assert title == "The Brass Compass"
    assert content == "A brass compass spun wildly beneath the aurora."


def test_parse_story_response_thinking_tags():
    raw = "<thought>Drafting title and content</thought>\nTITLE: Starlight Sonata\nCONTENT:\nMusic echoed through space."
    title, content = ai_service.parse_story_response(raw)
    assert title == "Starlight Sonata"
    assert content == "Music echoed through space."


def test_parse_story_response_fallback_title():
    raw = "Once upon a time on a silent moon, stars watched in stillness."
    title, content = ai_service.parse_story_response(raw, fallback_genre="Sci-Fi", fallback_mood="Peaceful")
    assert title == "A Peaceful Sci-Fi Tale"
    assert "Once upon a time" in content


def test_parse_story_response_empty_raises():
    with pytest.raises(ai_service.EmptyResponseError):
        ai_service.parse_story_response("")


# ---------------------------------------------------------------------------
# 3. Image Validation & Size Limit Tests
# ---------------------------------------------------------------------------
def test_image_validation_valid_png():
    raw, mime, ext = image_service.validate_and_decode_base64_image(VALID_B64_PNG)
    assert raw == TINY_PNG_BYTES
    assert mime == "image/png"
    assert ext == "png"


def test_image_validation_data_uri_prefix():
    data_uri = f"data:image/png;base64,{VALID_B64_PNG}"
    raw, mime, ext = image_service.validate_and_decode_base64_image(data_uri)
    assert raw == TINY_PNG_BYTES
    assert mime == "image/png"


def test_image_validation_invalid_base64():
    with pytest.raises(image_service.InvalidImageError):
        image_service.validate_and_decode_base64_image("%%%not_valid_base64%%%")


def test_image_validation_unsupported_format():
    # Plain text encoded in base64
    fake_img = base64.b64encode(b"This is just plain text, not an image!").decode("utf-8")
    with pytest.raises(image_service.UnsupportedImageError):
        image_service.validate_and_decode_base64_image(fake_img)


def test_image_validation_oversized_image():
    # Construct base64 payload larger than 5 MB
    large_payload = b"\x89PNG\r\n\x1a\n" + b"\x00" * (5 * 1024 * 1024 + 10)
    large_b64 = base64.b64encode(large_payload).decode("utf-8")
    with pytest.raises(image_service.ImageTooLargeError):
        image_service.validate_and_decode_base64_image(large_b64)


# ---------------------------------------------------------------------------
# 4. Generation Endpoint Workflow Tests (Mocked AI Service for Unit Isolation)
# ---------------------------------------------------------------------------
@patch("app.services.ai_service.generate_story")
def test_generation_workflow_text_only_success(mock_generate, client: TestClient):
    """Successful text-only generation persists to SQLite and returns 201."""
    mock_generate.return_value = (
        "The Starlight Compass",
        "A lone astronomer uncovered a compass that pointed towards memories instead of north.",
    )

    res = client.post("/api/stories/generate", json={
        "prompt": "An astronomer finds a magical compass.",
        "genre": "Fantasy",
        "mood": "Mysterious",
        "length": "Short",
    })

    assert res.status_code == status.HTTP_201_CREATED
    data = res.json()
    assert data["title"] == "The Starlight Compass"
    assert data["genre"] == "Fantasy"
    assert data["mood"] == "Mysterious"
    assert data["length"] == "Short"
    assert data["image_filename"] is None
    assert "id" in data
    assert "created_at" in data

    # Verify persisted in SQLite
    get_res = client.get(f"/api/stories/{data['id']}")
    assert get_res.status_code == status.HTTP_200_OK
    assert get_res.json()["title"] == "The Starlight Compass"


@patch("app.services.ai_service.generate_story")
def test_generation_workflow_image_only_success(mock_generate, client: TestClient):
    """Successful image-only generation stores image file, persists story with filename."""
    mock_generate.return_value = (
        "The Crimson Beacon",
        "High atop the cliffs, a crimson light shone against the rising tides.",
    )

    res = client.post("/api/stories/generate", json={
        "image_base64": VALID_B64_PNG,
        "genre": "Adventure",
        "mood": "Exciting",
        "length": "Short",
    })

    assert res.status_code == status.HTTP_201_CREATED
    data = res.json()
    assert data["title"] == "The Crimson Beacon"
    assert data["image_filename"] is not None
    assert data["image_filename"].endswith(".png")

    # Clean up test uploaded image
    image_service.cleanup_image_file(data["image_filename"])


@patch("app.services.ai_service.generate_story")
def test_generation_workflow_text_and_image_success(mock_generate, client: TestClient):
    """Combined text + image generation saves both prompt and image reference."""
    mock_generate.return_value = (
        "Island of Whispers",
        "The travelers landed their wooden skiff upon the shore guided by the map.",
    )

    res = client.post("/api/stories/generate", json={
        "prompt": "Expedition to an uncharted island.",
        "image_base64": VALID_B64_PNG,
        "genre": "Adventure",
        "mood": "Exciting",
        "length": "Medium",
    })

    assert res.status_code == status.HTTP_201_CREATED
    data = res.json()
    assert data["prompt"] == "Expedition to an uncharted island."
    assert data["image_filename"] is not None

    image_service.cleanup_image_file(data["image_filename"])


@patch("app.services.ai_service.generate_story")
def test_generation_failure_does_not_save_to_database(mock_generate, client: TestClient):
    """If generation fails (e.g. QuotaExceededError), no story should be written to SQLite."""
    mock_generate.side_effect = ai_service.QuotaExceededError("Rate limit exceeded")

    count_before = len(client.get("/api/stories").json())

    res = client.post("/api/stories/generate", json={
        "prompt": "This generation will fail due to quota.",
        "genre": "Fantasy",
        "mood": "Mysterious",
        "length": "Short",
    })

    assert res.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    count_after = len(client.get("/api/stories").json())
    assert count_after == count_before


@patch("app.services.ai_service.generate_story")
def test_generation_missing_api_key_returns_503(mock_generate, client: TestClient):
    """Missing API key returns 503 Service Unavailable."""
    mock_generate.side_effect = ai_service.MissingApiKeyError("API key not configured")

    res = client.post("/api/stories/generate", json={
        "prompt": "A magical journey.",
        "genre": "Fantasy",
        "mood": "Mysterious",
        "length": "Short",
    })

    assert res.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert "not configured" in res.text.lower()


@patch("app.services.ai_service.generate_story")
def test_generation_invalid_api_key_returns_401(mock_generate, client: TestClient):
    """Invalid API key returns 401 Unauthorized."""
    mock_generate.side_effect = ai_service.InvalidApiKeyError("Invalid API key")

    res = client.post("/api/stories/generate", json={
        "prompt": "A magical journey.",
        "genre": "Fantasy",
        "mood": "Mysterious",
        "length": "Short",
    })

    assert res.status_code == status.HTTP_401_UNAUTHORIZED
    assert "invalid" in res.text.lower()
