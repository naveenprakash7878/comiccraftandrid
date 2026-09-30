from app.models import (
    ComicLayout,
    ComicOutline,
    ComicStory,
    PromptRequest
)

from app.services.image_generator import (
    generate_image
)


def build_comic_layout(
    request: PromptRequest,
    outline: ComicOutline,
    story: ComicStory
) -> ComicLayout:

    story_by_number = {
        panel.panel_number: panel
        for panel in story.panels
    }

    panels = []

    for outline_panel in sorted(
        outline.panels,
        key=lambda panel:
        panel.panel_number
    ):

        story_panel = story_by_number.get(
            outline_panel.panel_number
        )

        if not story_panel:

            raise RuntimeError(
                "Missing story content for "
                f"panel {outline_panel.panel_number}."
            )

        image_url = generate_image(
            outline_panel.image_prompt,
            outline_panel.panel_number
        )

        panels.append({

            "panel_number":
                outline_panel.panel_number,

            "title":
                outline_panel.title,

            "image_url":
                image_url,

            "scene_description":
                outline_panel.scene_description,

            "image_prompt":
                outline_panel.image_prompt,

            "caption":
                story_panel.caption,

            "narration":
                story_panel.narration,

            "dialogue":
                story_panel.dialogue
        })

    title = (
        f"{request.character_name}: "
        f"{request.story_prompt[:70]}"
    )

    return ComicLayout(

        title=title,

        character_name=
            request.character_name,

        setting=
            request.setting,

        tone=
            request.tone,

        art_style=
            request.art_style,

        panels=panels
    )