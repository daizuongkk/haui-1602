"""FastAPI application factory and ASGI entry point (`presentation.api.app:app`)."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.presentation.api.routes import router


def create_app() -> FastAPI:
    app = FastAPI(title="Điện Biên Weather Alert API", version="1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.API_CORS_ORIGINS,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if settings.AUDIO_ROOT.exists():
        app.mount("/audio", StaticFiles(directory=str(settings.AUDIO_ROOT)), name="audio")

    app.include_router(router)
    return app


app = create_app()
