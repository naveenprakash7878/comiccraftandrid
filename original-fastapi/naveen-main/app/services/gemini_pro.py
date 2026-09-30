from google import genai
from google.genai import types

from app.config import get_settings
from app.models import (
    ComicOutline,
    ComicStory,
    PromptRequest
)


def get_client() -> genai.Client:

    settings = get_settings()

    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    return genai.Client(
        api_key=settings.gemini_api_key
    )


def generate_story(
    request: PromptRequest,
    outline: ComicOutline
) -> ComicStory:

    settings = get_settings()

    outline_json = outline.model_dump_json(
        indent=2
    )

    prompt = f"""
Create a complete comic script from the following
five-panel outline.

ORIGINAL STORY:
{request.story_prompt}

MAIN CHARACTER:
{request.character_name}

SETTING:
{request.setting}

TONE:
{request.tone}

ART STYLE:
{request.art_style}

OUTLINE:
{outline_json}

REQUIREMENTS:

- Exactly 5 panels.
- Keep the same panel numbers.
- Maintain story continuity.
- Do not introduce contradictory characters.
- Do not change the setting unnecessarily.

For each panel create:

CAPTION:
A short comic-style environmental caption.

NARRATION:
Short prose explaining the action or emotion.

DIALOGUE:
Natural dialogue spoken by characters.

Keep the writing concise enough to fit on a comic page.

Return ONLY structured JSON matching the requested schema.
"""

    response = get_client().models.generate_content(
        model=settings.gemini_story_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.9,
            response_mime_type="application/json",
            response_schema=ComicStory,
        ),
    )

    if not response.parsed:
        raise RuntimeError(
            "Gemini returned no structured story."
        )

    return response.parsed