from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)


Tone = Literal[
    "light-hearted",
    "dramatic",
    "poetic",
    "funny"
]

ArtStyle = Literal[
    "anime",
    "pixel art",
    "comic book",
    "realistic"
]


class PromptRequest(BaseModel):

    model_config = ConfigDict(
        str_strip_whitespace=True
    )

    story_prompt: str = Field(
        min_length=5,
        max_length=2000
    )

    character_name: str = Field(
        min_length=1,
        max_length=80
    )

    setting: str = Field(
        min_length=1,
        max_length=120
    )

    tone: Tone = "light-hearted"

    art_style: ArtStyle = "comic book"


class PanelOutline(BaseModel):

    panel_number: int = Field(
        ge=1,
        le=5
    )

    title: str

    scene_description: str

    image_prompt: str


class ComicOutline(BaseModel):

    panels: list[PanelOutline] = Field(
        min_length=5,
        max_length=5
    )


class PanelStory(BaseModel):

    panel_number: int = Field(
        ge=1,
        le=5
    )

    caption: str

    narration: str

    dialogue: str = ""


class ComicStory(BaseModel):

    panels: list[PanelStory] = Field(
        min_length=5,
        max_length=5
    )


class ComicPanel(BaseModel):

    panel_number: int

    title: str

    image_url: str

    scene_description: str

    image_prompt: str

    caption: str

    narration: str

    dialogue: str = ""


class ComicLayout(BaseModel):

    title: str

    character_name: str

    setting: str

    tone: str

    art_style: str

    panels: list[ComicPanel]

    pdf_url: str | None = None


class ComicResponse(BaseModel):

    success: bool

    comic: ComicLayout