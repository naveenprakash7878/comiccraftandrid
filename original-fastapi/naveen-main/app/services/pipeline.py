from app.models import (
    ComicLayout,
    PromptRequest
)

from app.services.gemini_flash import (
    generate_outline
)

from app.services.gemini_pro import (
    generate_story
)

from app.services.layout_builder import (
    build_comic_layout
)


def generate_comic(
    request: PromptRequest
) -> ComicLayout:

    outline = generate_outline(
        request
    )

    story = generate_story(
        request,
        outline
    )

    comic = build_comic_layout(
        request,
        outline,
        story
    )

    return comic