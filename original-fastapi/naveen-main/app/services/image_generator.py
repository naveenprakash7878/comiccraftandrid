from __future__ import annotations

import re
import uuid
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.config import get_settings


def safe_filename(
    value: str
) -> str:

    value = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        value
    )

    value = value.strip("_")

    return value[:80] or "panel"


def create_placeholder(
    prompt: str,
    output: Path,
    panel_number: int
):

    settings = get_settings()

    image = Image.new(
        "RGB",
        (
            settings.image_width,
            settings.image_height
        ),
        "#191923"
    )

    draw = ImageDraw.Draw(image)

    try:

        title_font = ImageFont.truetype(
            "DejaVuSans-Bold.ttf",
            42
        )

        normal_font = ImageFont.truetype(
            "DejaVuSans.ttf",
            20
        )

    except OSError:

        title_font = ImageFont.load_default()
        normal_font = ImageFont.load_default()

    draw.text(
        (40, 40),
        f"COMIC PANEL {panel_number}",
        fill="white",
        font=title_font
    )

    draw.text(
        (40, 110),
        "Placeholder image mode",
        fill="#cccccc",
        font=normal_font
    )

    text = prompt[:900]

    y = 160

    for index in range(
        0,
        len(text),
        65
    ):

        line = text[index:index + 65]

        draw.text(
            (40, y),
            line,
            fill="#eeeeee",
            font=normal_font
        )

        y += 28

    image.save(
        output,
        format="PNG"
    )


def generate_huggingface_image(
    prompt: str,
    output: Path
):

    from huggingface_hub import (
        InferenceClient
    )

    settings = get_settings()

    if not settings.hf_token:

        raise RuntimeError(
            "HF_TOKEN is not configured."
        )

    client = InferenceClient(
        api_key=settings.hf_token,
        provider="auto"
    )

    image = client.text_to_image(
        prompt=prompt,
        model=settings.hf_image_model,
        width=settings.image_width,
        height=settings.image_height
    )

    image.save(output)


_local_pipeline = None


def generate_local_image(
    prompt: str,
    output: Path
):

    global _local_pipeline

    import torch

    from diffusers import (
        DiffusionPipeline
    )

    settings = get_settings()

    if _local_pipeline is None:

        dtype = (
            torch.float16
            if torch.cuda.is_available()
            else torch.float32
        )

        _local_pipeline = (
            DiffusionPipeline.from_pretrained(
                settings.local_diffusion_model,
                torch_dtype=dtype
            )
        )

        if torch.cuda.is_available():

            _local_pipeline.to("cuda")

        else:

            _local_pipeline.to("cpu")

    result = _local_pipeline(
        prompt,
        width=settings.image_width,
        height=settings.image_height,
        num_inference_steps=settings.image_steps
    )

    result.images[0].save(output)


def generate_image(
    prompt: str,
    panel_number: int
) -> str:

    settings = get_settings()

    filename = (
        f"{uuid.uuid4().hex[:12]}"
        f"_panel_{panel_number}_"
        f"{safe_filename(prompt[:40])}.png"
    )

    output = (
        settings.panels_dir /
        filename
    )

    enhanced_prompt = f"""
{prompt}

High quality comic illustration.
Consistent main character design.
Consistent clothing and appearance.
Strong facial expression.
Detailed environment.
Cinematic lighting.
Professional composition.
High detail.
Clean artwork.
No text.
No watermark.
No logo.
"""

    backend = (
        settings.image_backend
        .lower()
    )

    if backend == "placeholder":

        create_placeholder(
            enhanced_prompt,
            output,
            panel_number
        )

    elif backend == "hf":

        generate_huggingface_image(
            enhanced_prompt,
            output
        )

    elif backend == "local":

        generate_local_image(
            enhanced_prompt,
            output
        )

    else:

        raise RuntimeError(
            f"Unsupported IMAGE_BACKEND="
            f"'{settings.image_backend}'. "
            f"Use hf, local, or placeholder."
        )

    return (
        f"/static/panels/{filename}"
    )