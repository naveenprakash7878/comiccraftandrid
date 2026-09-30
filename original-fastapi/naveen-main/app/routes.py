from pathlib import Path
from urllib.parse import unquote

from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Request
)

from fastapi.templating import (
    Jinja2Templates
)

from fastapi.responses import (
    FileResponse
)

from app.config import get_settings

from app.models import (
    ComicResponse,
    PromptRequest
)

from app.services.exporters import (
    save_pdf
)

from app.services.image_generator import (
    generate_image
)

from app.services.pipeline import (
    generate_comic
)


router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)


@router.get("/")
async def home(
    request: Request
):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "error": None
        }
    )


def create_prompt_request(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str
) -> PromptRequest:

    try:

        return PromptRequest(

            story_prompt=story_prompt,

            character_name=character_name,

            setting=setting,

            tone=tone,

            art_style=art_style
        )

    except Exception as exc:

        raise HTTPException(
            status_code=422,
            detail=str(exc)
        ) from exc


@router.post("/generate")
async def generate_form(

    request: Request,

    story_prompt: str = Form(...),

    character_name: str = Form(...),

    setting: str = Form(...),

    tone: str = Form(...),

    art_style: str = Form(...)
):

    try:

        prompt_request = (
            create_prompt_request(
                story_prompt,
                character_name,
                setting,
                tone,
                art_style
            )
        )

        comic = generate_comic(
            prompt_request
        )

        comic.pdf_url = save_pdf(
            comic
        )

        return templates.TemplateResponse(

            request=request,

            name="comic_preview.html",

            context={
                "comic": comic,
                "error": None
            }
        )

    except Exception as exc:

        return templates.TemplateResponse(

            request=request,

            name="index.html",

            context={

                "error": str(exc),

                "form": {

                    "story_prompt":
                        story_prompt,

                    "character_name":
                        character_name,

                    "setting":
                        setting,

                    "tone":
                        tone,

                    "art_style":
                        art_style
                }
            },

            status_code=500
        )


@router.post(
    "/generate-comic/json",
    response_model=ComicResponse
)
async def generate_json(
    payload: PromptRequest
):

    try:

        comic = generate_comic(
            payload
        )

        comic.pdf_url = save_pdf(
            comic
        )

        return ComicResponse(
            success=True,
            comic=comic
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        ) from exc


@router.post("/test-image")
async def test_image(
    prompt: str = Form(...)
):

    try:

        image_url = generate_image(
            prompt,
            panel_number=0
        )

        return {
            "success": True,
            "image_url": image_url
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        ) from exc


@router.get(
    "/download/{filename}"
)
async def download_pdf(
    filename: str
):

    settings = get_settings()

    safe_filename = Path(
        unquote(filename)
    ).name

    pdf_path = (
        settings.exports_dir /
        safe_filename
    )

    if (
        not pdf_path.is_file()
        or pdf_path.suffix.lower() != ".pdf"
    ):

        raise HTTPException(
            status_code=404,
            detail="PDF not found."
        )

    return FileResponse(

        pdf_path,

        media_type="application/pdf",

        filename=safe_filename
    )


@router.get(
    "/export-success"
)
async def export_success(
    request: Request,
    filename: str | None = None
):

    return templates.TemplateResponse(

        request=request,

        name="export_success.html",

        context={
            "filename": filename
        }
    )