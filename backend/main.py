import logging
import shutil
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router, health_router_instance as health_router
from app.api.websocket import register_progress_callback, router as ws_router
from app.core.config import settings
from app.downloader.manager import start_manager

logger = logging.getLogger(__name__)

app = FastAPI(title="Universal Video Downloader", version="0.1.0")

# CORS: Allow frontend origins (local dev + production)
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
# Add production frontend URL from environment variable
if settings.FRONTEND_URL:
    allowed_origins.append(settings.FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(health_router)
app.include_router(ws_router)


@app.on_event("startup")
async def startup():
    # Enable debug logging for entire app (every file in the flow)
    _debug_loggers = (
        "app.core.config",
        "app.database.session",
        "app.database.repositories",
        "app.services.disk",
        "app.downloader.queue",
        "app.downloader.manager",
        "app.downloader.ytdlp_wrapper",
        "app.api.routes.extract",
        "app.api.routes.downloads",
        "app.api.routes.health",
        "app.api.routes.settings",
        "app.api.websocket",
    )
    for name in _debug_loggers:
        logging.getLogger(name).setLevel(logging.DEBUG)
    # Validate FFmpeg
    ffmpeg = shutil.which("ffmpeg") or (settings.FFMPEG_PATH if settings.FFMPEG_PATH else None)
    if not ffmpeg and settings.FFMPEG_PATH:
        ffmpeg = str(Path(settings.FFMPEG_PATH).resolve()) if Path(settings.FFMPEG_PATH).exists() else None
    if not ffmpeg:
        logger.warning("FFmpeg not found on PATH or FFMPEG_PATH; some downloads may fail.")
    # Validate yt-dlp
    try:
        import yt_dlp  # noqa: F401
    except ImportError:
        raise RuntimeError("yt-dlp not installed. Run: pip install yt-dlp")
    await start_manager()
    register_progress_callback()


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.BIND, port=settings.PORT, reload=True)
