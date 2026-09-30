from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from fpdf import FPDF
from PIL import Image

from app.config import get_settings
from app.models import ComicLayout


def clean_text(
    value: str
) -> str:

    return (
        value
        .encode("latin-1", "replace")
        .decode("latin-1")
    )


def get_local_image(
    image_url: str
) -> Path:

    settings = get_settings()

    prefix = "/static/panels/"

    if not image_url.startswith(prefix):

        raise ValueError(
            "Invalid image URL."
        )

    filename = Path(
        image_url[len(prefix):]
    ).name

    image_path = (
        settings.panels_dir /
        filename
    )

    if not image_path.is_file():

        raise FileNotFoundError(
            f"Panel image not found: {filename}"
        )

    return image_path


def save_pdf(
    layout: ComicLayout
) -> str:

    settings = get_settings()

    timestamp = datetime.now(
        timezone.utc
    ).strftime(
        "%Y%m%d_%H%M%S"
    )

    safe_name = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        layout.character_name
    )[:40]

    filename = (
        f"comic_{safe_name}_"
        f"{timestamp}.pdf"
    )

    output = (
        settings.exports_dir /
        filename
    )

    pdf = FPDF()

    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )

    for panel in layout.panels:

        pdf.add_page()

        pdf.set_font(
            "Helvetica",
            "B",
            18
        )

        pdf.multi_cell(
            0,
            10,
            clean_text(
                f"Panel {panel.panel_number}: "
                f"{panel.title}"
            )
        )

        image_path = get_local_image(
            panel.image_url
        )

        x = 15

        y = (
            pdf.get_y() +
            5
        )

        max_width = 180
        max_height = 105

        with Image.open(
            image_path
        ) as image:

            width, height = (
                image.size
            )

        scale = min(
            max_width / width,
            max_height / height
        )

        display_width = (
            width * scale
        )

        display_height = (
            height * scale
        )

        pdf.image(
            str(image_path),
            x=x,
            y=y,
            w=display_width,
            h=display_height
        )

        pdf.set_y(
            y +
            display_height +
            8
        )

        pdf.set_font(
            "Helvetica",
            "I",
            10
        )

        pdf.multi_cell(
            0,
            6,
            clean_text(
                panel.scene_description
            )
        )

        pdf.ln(2)

        if panel.caption:

            pdf.set_font(
                "Helvetica",
                "B",
                11
            )

            pdf.multi_cell(
                0,
                7,
                clean_text(
                    f"Caption: "
                    f"{panel.caption}"
                )
            )

        if panel.narration:

            pdf.set_font(
                "Helvetica",
                "",
                11
            )

            pdf.multi_cell(
                0,
                7,
                clean_text(
                    f"Narration: "
                    f"{panel.narration}"
                )
            )

        if panel.dialogue:

            pdf.set_font(
                "Helvetica",
                "B",
                11
            )

            pdf.multi_cell(
                0,
                7,
                clean_text(
                    f"Dialogue: "
                    f"{panel.dialogue}"
                )
            )

    pdf.output(
        str(output)
    )

    return (
        f"/static/exports/{filename}"
    )