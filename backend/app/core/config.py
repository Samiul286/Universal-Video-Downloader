"""Application configuration. Single source of truth for env vars."""
import logging
from pathlib import Path
from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


def _system_downloads() -> Path:
    return Path.home() / "Downloads"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PORT: int = 8000
    BIND: str = "0.0.0.0"
    DOWNLOAD_PATH: Optional[str] = None  # Optional; effective path from get_effective_download_path()
    DB_PATH: str = "./storage/downloader.db"
    MAX_CONCURRENT: int = 2
    QUEUE_MAX_SIZE: int = 100
    FFMPEG_PATH: Optional[str] = None
    PROXY: Optional[str] = None
    COOKIES_PATH: Optional[str] = None
    FRONTEND_URL: Optional[str] = None  # Production frontend URL for CORS

    @field_validator("DB_PATH", mode="before")
    @classmethod
    def normalize_db_path(cls, v: str) -> str:
        if not v:
            return v
        return str(Path(v).resolve())

    @property
    def db_path_resolved(self) -> Path:
        return Path(self.DB_PATH)


settings = Settings()


def get_effective_download_path(
    *,
    request_path: Optional[str] = None,
    settings_path: Optional[str] = None,
) -> Optional[Path]:
    """
    Resolve where to save downloads (Section 2 "Download folder behavior").
    Order: (a) request_path if provided and valid, (b) settings_path (persisted) if folder exists,
    (c) env DOWNLOAD_PATH if set and exists, (d) system Downloads if exists; else None.
    """
    settings = Settings()
    candidates: list[Optional[str]] = [request_path, settings_path, settings.DOWNLOAD_PATH]
    logger.info("[DEBUG] get_effective_download_path request_path=%s settings_path=%s env_DOWNLOAD_PATH=%s", request_path, settings_path, settings.DOWNLOAD_PATH)
    for c in candidates:
        if not c:
            continue
        p = Path(c).resolve()
        if p.is_dir():
            logger.info("[DEBUG] get_effective_download_path resolved effective=%s (from candidate %s)", p, c)
            return p
        logger.debug("[DEBUG] get_effective_download_path skip (not dir): %s", p)
    sys_dl = _system_downloads()
    if sys_dl.is_dir():
        logger.info("[DEBUG] get_effective_download_path resolved effective=%s (system Downloads)", sys_dl)
        return sys_dl
    logger.warning("[DEBUG] get_effective_download_path no valid path (returning None)")
    return None
