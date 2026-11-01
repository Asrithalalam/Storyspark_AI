"""Gemma 4 AI model integration service for creative story generation."""

import logging
import re
import time
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


# Model identifiers
VISION_MODEL_ID = "gemini-3.5-flash"

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
    visual_details: str | None = None,
) -> str:
    """
    Construct the tailored generation prompt for the Gemma model.
    Enforces genre, mood, target length, simple vocabulary, fresh character naming,
    and strict output formatting.
    """
    length_spec = LENGTH_TARGETS.get(length, LENGTH_TARGETS["Short"])
    word_range = length_spec["range"]

    if prompt and visual_details:
        grounding = (
            f"Combine and weave together these two sources of inspiration:\n"
            f"- Written Idea: \"{prompt}\"\n"
            f"- Visual Inspiration from uploaded image: {visual_details}\n"
            f"Ensure the story prominently incorporates both the written idea and the specific visual setting, objects, and atmosphere."
        )
    elif visual_details:
        grounding = (
            f"Build the entire story around this visual inspiration from the uploaded image:\n"
            f"{visual_details}\n"
            f"Bring the setting, characters, objects, and atmosphere described in the visual inspiration vividly to life in the narrative."
        )
    else:
        grounding = f"Develop this creative premise into a complete story:\n\"{prompt}\""

    return f"""You are StorySpark AI, a creative storyteller who writes clear, captivating stories.
Write an original, complete story following these instructions:

- Genre: {genre}
- Mood / Feeling: {mood}
- Target Length: {word_range} (keep the word count close to this range)
- Narrative Structure: A clear story with an engaging beginning, a meaningful middle event or problem, and a satisfying ending.
- Story Premise: {grounding}

WRITING STYLE GUIDELINES:
1. Simple, Natural English:
   - Use simple, everyday, commonly understood English.
   - Prefer short, clear sentences.
   - Use familiar vocabulary. Avoid unnecessarily fancy or complex words (for example, do not use words like "iridescent", "ethereal", "sentinel", or "melodic resonance" when plain, natural words tell the story better).
   - Avoid piling on adjectives or overly decorative descriptions. Choose clear, concrete actions and descriptions that are easy to picture.
   - Keep dialogue natural, expressive, and easy to follow.
   - Maintain emotional warmth and depth without making the story childish or dull.

2. Fresh and Varied Character Names:
   - Pick original, natural names that fit the story's setting and genre.
   - Do NOT repeatedly default to common stock names (such as "Elara", "Pip", "Barnaby", or "Lyra"). Choose fresh names for each new story.
   - If regenerating from the same premise, introduce distinct characters and a different angle of events rather than repeating the same names or exact plot beats.

STRICT OUTPUT FORMAT RULES:
1. First line: Output 'TITLE: <Story Title>'.
2. Second line: Output 'CONTENT:'.
3. Follow immediately with the story text in clean paragraphs.
4. Do NOT output any introductory remarks, prefaces, conversational greetings, or concluding author notes.
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


# GenAI client instance cache to reuse transport and connection pools
_cached_client: genai.Client | None = None
_cached_client_key: str | None = None


def get_genai_client(api_key: str) -> genai.Client:
    """Return a cached GenAI client instance to reuse connection pools and avoid re-initialization overhead."""
    global _cached_client, _cached_client_key
    if _cached_client is None or _cached_client_key != api_key:
        _cached_client = genai.Client(api_key=api_key)
        _cached_client_key = api_key
    return _cached_client


def extract_visual_details(client: genai.Client, image_bytes: bytes, mime_type: str) -> str:
    """
    Extract key visual details, subjects, setting, mood, and objects from an image
    using the vision model to ground the narrative prompt for Gemma 4.

    Args:
        client: Authenticated GenAI client instance.
        image_bytes: Raw decoded image bytes.
        mime_type: MIME type of the image (e.g. image/png, image/jpeg).

    Returns:
        String describing the visual elements of the image.

    Raises:
        InvalidApiKeyError: If API key is rejected.
        QuotaExceededError: If rate limit is exceeded.
        AiProviderError: If the image analysis fails.
    """
    image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    vision_prompt = (
        "Carefully describe this image for a creative storyteller. Detail the primary subjects, "
        "objects, setting, atmospheric mood, distinctive lighting, and colors in 2 to 3 vivid sentences."
    )

    vision_resp = None
    for attempt in range(2):
        try:
            vision_resp = client.models.generate_content(
                model=VISION_MODEL_ID,
                contents=[image_part, vision_prompt],
            )
            break
        except genai_errors.ServerError as exc:
            if attempt == 0:
                logger.warning(f"Transient ServerError during image analysis, retrying in 1s: {exc}")
                time.sleep(1.0)
                continue
            logger.error(f"Vision API ServerError: {exc}")
            raise AiProviderError("The AI model service encountered a temporary error during image analysis. Please try again later.") from None
        except genai_errors.ClientError as exc:
            err_str = str(exc).lower()
            logger.error(f"Vision API ClientError: {exc}")
            if "api key not valid" in err_str or "invalid_argument" in err_str and "api_key" in err_str:
                raise InvalidApiKeyError("Invalid API key provided for image analysis.") from None
            if "resource_exhausted" in err_str or "quota" in err_str:
                raise QuotaExceededError("AI generation quota or rate limit exceeded during image analysis.") from None
            raise AiProviderError(f"Image analysis request error: {exc}") from None
        except Exception as exc:
            logger.error(f"Failed to analyze image: {exc}")
            raise AiProviderError("Failed to analyze the uploaded image. Please try again.") from None

    details = getattr(vision_resp, "text", "") or ""
    details = details.strip()
    if not details:
        logger.error("Vision model returned empty visual details.")
        raise EmptyResponseError("Image analysis returned empty visual details.")

    logger.info(f"Successfully extracted visual details: {details[:80]}...")
    return details


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
    Uses ThinkingLevel.MINIMAL to ensure rapid generation while preserving narrative quality.
    For image inputs, extracts visual details via the vision pipeline to ground Gemma 4's writing.

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
    logger.info(f"Using GenAI client for model '{model_id}' (has_image={bool(image_bytes)})")

    try:
        client = get_genai_client(api_key)
    except Exception as exc:
        logger.error(f"Failed to initialize GenAI client: {exc}")
        raise AiProviderError("Failed to initialize AI model client.") from None

    # Step 1: If an image is provided, extract visual details to ground the story
    visual_details = None
    if image_bytes and mime_type:
        visual_details = extract_visual_details(
            client=client,
            image_bytes=image_bytes,
            mime_type=mime_type,
        )

    # Step 2: Construct prompt instructions for Gemma 4
    prompt_text = build_generation_prompt(
        prompt=prompt,
        genre=genre,
        mood=mood,
        length=length,
        visual_details=visual_details,
    )

    # Configure Gemma 4 with ThinkingLevel.MINIMAL for high-speed generation
    gemma_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level=types.ThinkingLevel.MINIMAL
        )
    )

    response = None
    for attempt in range(2):
        try:
            response = client.models.generate_content(
                model=model_id,
                contents=[prompt_text],
                config=gemma_config,
            )
            break
        except genai_errors.ServerError as exc:
            if attempt == 0:
                logger.warning(f"Transient ServerError from Gemma API, retrying in 1.5s: {exc}")
                time.sleep(1.5)
                continue
            logger.error(f"GenAI ServerError: {exc}")
            raise AiProviderError("The AI model service encountered a temporary error. Please try again later.") from None
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
