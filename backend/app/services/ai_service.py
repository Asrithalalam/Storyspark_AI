"""Gemma 4 AI model integration service for creative story generation."""

import logging
import re
from typing import Tuple

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from app.config import settings

logger = logging.getLogger(__name__)


# Custom exceptions for fine-grained error handling and HTTP status mapping
class AiServiceError(Exception):
    """Base exception for AI generation service."""
    pass


class MissingApiKeyError(AiServiceError):
    """Raised when the API key is not configured."""
    pass


class InvalidApiKeyError(AiServiceError):
    """Raised when the API key is rejected by the provider."""
    pass


class QuotaExceededError(AiServiceError):
    """Raised when the provider rate limit or quota is exhausted."""
    pass


class AiTimeoutError(AiServiceError):
    """Raised when the AI model call times out."""
    pass


class EmptyResponseError(AiServiceError):
    """Raised when the model returns an empty or unparseable response."""
    pass


class AiProviderError(AiServiceError):
    """Raised when the provider returns a server or execution error."""
    pass


LENGTH_TARGETS: dict[str, dict[str, str | int]] = {
    "Short": {"range": "150-200 words", "target": 175},
    "Medium": {"range": "250-350 words", "target": 300},
    "Long": {"range": "450-550 words", "target": 500},
}


def build_generation_prompt(
    prompt: str | None,
    genre: str,
    mood: str,
    length: str,
    has_image: bool = False,
) -> str:
    """
    Construct the tailored generation prompt for the Gemma model.
    Enforces genre, mood, target length, and strict output formatting.
    """
    length_spec = LENGTH_TARGETS.get(length, LENGTH_TARGETS["Short"])
    word_range = length_spec["range"]

    if prompt and has_image:
        grounding = (
            f"Harmoniously combine the visual details, mood, and characters observed in the provided image "
            f"with this creative premise:\n\"{prompt}\""
        )
    elif has_image:
        grounding = (
            "Carefully observe the provided image. Ground the entire narrative in the visual details, setting, "
            "atmosphere, and evocative elements visible in the image."
        )
    else:
        grounding = f"Expand upon and bring to life this creative premise:\n\"{prompt}\""

    return f"""You are StorySpark AI, a master creative storyteller.
Craft a complete, original, and captivating narrative that strictly adheres to these creative constraints:

- Genre: {genre}
- Mood / Atmosphere: {mood}
- Target Length: {word_range} (aim close to this range)
- Narrative Structure: A cohesive story featuring an engaging beginning, compelling middle, and satisfying resolution.
- Language: Natural, vivid, and evocative English matching the requested {mood} atmosphere.
- Grounding: {grounding}

STRICT OUTPUT FORMAT RULES:
1. On the very first line, output the story title starting with 'TITLE: ' (e.g. TITLE: The Whispering Forest).
2. On the next line, output 'CONTENT:'.
3. Follow immediately with the complete story narrative.
4. Do NOT output any intro remarks, author notes, conversational commentary, or meta-explanations.
"""


def parse_story_response(
    raw_text: str,
    fallback_genre: str = "Story",
    fallback_mood: str = "Creative",
) -> Tuple[str, str]:
    """
    Parse the AI model's response to separate the title from the story content.
    Resilient to diverse formatting variations, markdown hashes, or missing prefixes.

    Args:
        raw_text: Raw string response from Gemma.
        fallback_genre: Genre used for fallback title generation.
        fallback_mood: Mood used for fallback title generation.

    Returns:
        Tuple of (title, content).

    Raises:
        EmptyResponseError: If no usable story content is found.
    """
    if not raw_text or not raw_text.strip():
        raise EmptyResponseError("The AI model returned an empty response.")

    # Strip reasoning tags if returned by reasoning models (<thought>...</thought>)
    cleaned = re.sub(r"<thought>.*?</thought>", "", raw_text, flags=re.DOTALL).strip()
    if not cleaned:
        raise EmptyResponseError("The AI model response contained no narrative content.")

    # 1. Attempt to match the standardized TITLE: and CONTENT: format
    title_match = re.search(r"(?i)^title\s*:\s*(.*?)$", cleaned, flags=re.MULTILINE)
    content_match = re.search(r"(?i)\bcontent\s*:\s*(.*)$", cleaned, flags=re.DOTALL)

    if title_match and content_match:
        title = title_match.group(1).strip().strip('*\"# \t')
        content = content_match.group(1).strip()
        if title and content:
            return title, content

    # 2. Fallback: Inspect the first non-empty line as a potential title
    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    if not lines:
        raise EmptyResponseError("No readable content could be extracted from the AI response.")

    first_line = lines[0].strip('*\"# \t')
    # If the first line is short and does not terminate like a regular prose sentence
    if len(first_line) < 80 and not first_line.endswith((".", "!", "?")) and len(lines) > 1:
        title = first_line
        content = "\n\n".join(lines[1:]).strip()
        if content:
            return title, content

    # 3. Fallback: Generate a clean descriptive title from metadata
    fallback_title = f"A {fallback_mood} {fallback_genre} Tale"
    return fallback_title, cleaned


def generate_story(
    prompt: str | None,
    image_bytes: bytes | None = None,
    mime_type: str | None = None,
    genre: str = "Fantasy",
    mood: str = "Mysterious",
    length: str = "Short",
) -> Tuple[str, str]:
    """
    Send prompt and optional image to Gemma 4 via the Google GenAI SDK.

    Args:
        prompt: Optional text premise.
        image_bytes: Optional decoded image bytes.
        mime_type: MIME type of the image (e.g. image/png).
        genre: Target genre.
        mood: Target mood.
        length: Target length ('Short', 'Medium', 'Long').

    Returns:
        Tuple of (title, story_content).

    Raises:
        MissingApiKeyError: If GEMINI_API_KEY is not set.
        InvalidApiKeyError: If API key is rejected (401/400).
        QuotaExceededError: If rate limit is hit (429).
        AiTimeoutError: If request times out.
        EmptyResponseError: If model response is empty.
        AiProviderError: For any provider server errors.
    """
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        logger.error("GEMINI_API_KEY is not configured in environment.")
        raise MissingApiKeyError(
            "Gemma API key is not configured. Please set GEMINI_API_KEY in backend/.env."
        )

    model_id = settings.GEMMA_MODEL_ID
    logger.info(f"Initializing GenAI client for model '{model_id}' (has_image={bool(image_bytes)})")

    try:
        client = genai.Client(api_key=api_key)
    except Exception as exc:
        logger.error(f"Failed to initialize GenAI client: {exc}")
        raise AiProviderError("Failed to initialize AI model client.") from None

    # Construct prompt instructions
    prompt_text = build_generation_prompt(
        prompt=prompt,
        genre=genre,
        mood=mood,
        length=length,
        has_image=bool(image_bytes),
    )

    contents = []
    if image_bytes and mime_type:
        image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        contents.append(image_part)

    contents.append(prompt_text)

    try:
        response = client.models.generate_content(
            model=model_id,
            contents=contents,
        )
    except genai_errors.ClientError as exc:
        err_str = str(exc).lower()
        logger.error(f"GenAI ClientError: {exc}")
        if "api key not valid" in err_str or "invalid_argument" in err_str and "api_key" in err_str:
            raise InvalidApiKeyError("Invalid API key provided for Gemma API.") from None
        if "resource_exhausted" in err_str or "quota" in err_str:
            raise QuotaExceededError("AI generation quota or rate limit exceeded. Please try again later.") from None
        if "permission_denied" in err_str:
            raise InvalidApiKeyError("Permission denied for the requested AI model.") from None
        raise AiProviderError(f"AI client request error: {exc}") from None
    except genai_errors.ServerError as exc:
        logger.error(f"GenAI ServerError: {exc}")
        raise AiProviderError("The AI model service encountered a temporary error. Please try again later.") from None
    except genai_errors.APIError as exc:
        logger.error(f"GenAI APIError: {exc}")
        err_str = str(exc).lower()
        if "quota" in err_str or "resource_exhausted" in err_str or exc.code == 429:
            raise QuotaExceededError("AI generation quota exceeded.") from None
        raise AiProviderError("AI service provider returned an error.") from None
    except TimeoutError as exc:
        logger.error(f"AI request timed out: {exc}")
        raise AiTimeoutError("The request to the AI model timed out. Please try again.") from None
    except Exception as exc:
        logger.error(f"Unexpected error communicating with AI model: {exc}")
        raise AiProviderError(f"Unexpected error during story generation: {exc}") from None

    # Check response text
    raw_text = getattr(response, "text", None)
    if not raw_text and hasattr(response, "candidates") and response.candidates:
        first_candidate = response.candidates[0]
        if hasattr(first_candidate, "content") and hasattr(first_candidate.content, "parts"):
            part_texts = [p.text for p in first_candidate.content.parts if getattr(p, "text", None)]
            raw_text = "".join(part_texts)

    if not raw_text or not raw_text.strip():
        logger.error("AI model returned empty response content.")
        raise EmptyResponseError("The AI model returned an empty story response.")

    title, content = parse_story_response(raw_text, fallback_genre=genre, fallback_mood=mood)
    return title, content
