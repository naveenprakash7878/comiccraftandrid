from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "ComicCraft"
    environment: str = "development"
    debug: bool = True

    # Gemini
    gemini_api_key: str | None = None
    gemini_outline_model: str = "gemini-3.8-flash"
    gemini_story_model: str = "gemini-3.8-flash"

    # Hugging Face
    hf_token: str | None = None
    image_backend: str = "hf"

    hf_image_model: str = (
        "stabilityai/stable-diffusion-xl-base-1.0"
    )

    # Local Diffusers
    local_diffusion_model: str = (
        "runwayml/stable-diffusion-v1-5"
    )

    image_width: int = 768
    image_height: int = 768
    image_steps: int = 25

    output_dir: Path = BASE_DIR / "app" / "static"

    panels_dir: Path = (
        BASE_DIR / "app" / "static" / "panels"
    )

    exports_dir: Path = (
        BASE_DIR / "app" / "static" / "exports"
    )

    max_prompt_length: int = 2000
    max_character_length: int = 80
    max_setting_length: int = 120

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    settings = Settings()

    settings.panels_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    settings.exports_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    return settings