from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routes import router


settings = get_settings()


app = FastAPI(

    title=settings.app_name,

    description=(
        "AI Comic Story Creator "
        "using Gemini and diffusion models."
    ),

    version="1.0.0"
)


app.mount(

    "/static",

    StaticFiles(
        directory="app/static"
    ),

    name="static"
)


app.include_router(
    router
)


@app.get("/health")
async def health():

    return {

        "status": "ok",

        "service":
            settings.app_name,

        "image_backend":
            settings.image_backend,

        "gemini_configured":
            bool(
                settings.gemini_api_key
            ),

        "huggingface_configured":
            bool(
                settings.hf_token
            )
    }