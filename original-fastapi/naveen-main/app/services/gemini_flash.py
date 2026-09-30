from google import genai
from google.genai import types

from app.config import get_settings
from app.models import (
    ComicOutline,
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


def generate_outline(
    request: PromptRequest
) -> ComicOutline:

    settings = get_settings()

    prompt = f"""
Create a coherent 5-panel comic outline.

USER STORY:
{request.story_prompt}

MAIN CHARACTER:
{request.character_name}

SETTING:
{request.setting}

TONE:
{request.tone}

ART STYLE:
{request.art_style}

IMPORTANT REQUIREMENTS:

1. Create exactly 5 panels.
2. Number panels from 1 to 5.
3. Maintain the same protagonist throughout.
4. Give every panel a short title.
5. Give every panel a scene description.
6. Give every panel a detailed image generation prompt.
7. Keep the story visually consistent.
8. Create a clear beginning.
9. Create an escalation.
10. Create a turning point.
11. Create a satisfying ending.
12. Do not put readable text inside generated artwork.
13. Do not add watermarks.
14. Preserve the protagonist's appearance between panels.

Each image prompt should describe:

- character appearance
- pose
- facial expression
- environment
- lighting
- camera angle
- composition
- action
- art style

Return ONLY structured JSON matching the requested schema.
"""

    response = get_client().models.generate_content(
        model=settings.gemini_outline_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.8,
            response_mime_type="application/json",
            response_schema=ComicOutline,
        ),
    )

    if not response.parsed:
        raise RuntimeError(
            "Gemini returned no structured outline."
        )

    return response.parsed