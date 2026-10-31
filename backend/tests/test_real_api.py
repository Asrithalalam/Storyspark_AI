"""Real integration tests with Google Gemma 4 model (gemma-4-26b-a4b-it).

Note: These tests require a valid GEMINI_API_KEY in backend/.env.
If GEMINI_API_KEY is not set, they are automatically skipped without faking results.
"""

from pathlib import Path
import pytest
from app.config import settings
from app.services.ai_service import generate_story

# Meaningful sample image fixture (343x361 PNG)
FIXTURE_IMAGE_PATH = Path(__file__).parent / "fixtures" / "sample_story_image.png"

if FIXTURE_IMAGE_PATH.exists():
    SAMPLE_IMAGE_BYTES = FIXTURE_IMAGE_PATH.read_bytes()
else:
    # Minimal fallback if fixture is not present
    SAMPLE_IMAGE_BYTES = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
        b"\x00\x00\x00\rIDATx\x9cc\xf8\xff\xff?\x03\x00\x08\xfc\x02\xfe\xa7\x9a\xa0\xa0\x00\x00\x00\x00IEND\xaeB`\x82"
    )


@pytest.fixture(autouse=True)
def require_api_key():
    """Skip test if GEMINI_API_KEY is not configured in backend/.env."""
    if not settings.GEMINI_API_KEY:
        pytest.skip("Real API integration test skipped: GEMINI_API_KEY is not set in backend/.env")


def test_real_api_text_only():
    """Real API test: generate a story from text prompt only."""
    title, content = generate_story(
        prompt="A clockmaker invents a pocket watch that pauses raindrops.",
        image_bytes=None,
        mime_type=None,
        genre="Fantasy",
        mood="Whimsical",
        length="Short",
    )
    assert title and len(title) > 0
    assert content and len(content) > 50
    print(f"\n[Real API Text-Only Result]\nTitle: {title}\nContent:\n{content}\n")


def test_real_api_image_only():
    """Real API test: generate a story grounded purely in image input."""
    title, content = generate_story(
        prompt=None,
        image_bytes=SAMPLE_IMAGE_BYTES,
        mime_type="image/png",
        genre="Fantasy",
        mood="Whimsical",
        length="Short",
    )
    assert title and len(title) > 0
    assert content and len(content) > 50
    print(f"\n[Real API Image-Only Result]\nTitle: {title}\nContent:\n{content}\n")


def test_real_api_text_and_image():
    """Real API test: generate a story combining text prompt and image input."""
    title, content = generate_story(
        prompt="A traveler discovers a secret doorway glowing in the dusk.",
        image_bytes=SAMPLE_IMAGE_BYTES,
        mime_type="image/png",
        genre="Adventure",
        mood="Exciting",
        length="Short",
    )
    assert title and len(title) > 0
    assert content and len(content) > 50
    print(f"\n[Real API Text+Image Result]\nTitle: {title}\nContent:\n{content}\n")
