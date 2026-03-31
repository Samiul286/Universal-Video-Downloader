from pydantic import BaseModel, HttpUrl
from typing import Any, Optional


class ExtractRequest(BaseModel):
    url: HttpUrl
    cookies: Optional[str] = None  # Netscape-format cookies (per-user); overrides COOKIES_PATH for this request


class FormatItem(BaseModel):
    format_id: str
    ext: Optional[str] = None
    resolution: Optional[str] = None
    filesize: Optional[int] = None
    vcodec: Optional[str] = None
    acodec: Optional[str] = None


class PlaylistEntry(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    url: str


class ExtractResponse(BaseModel):
    title: str
    thumbnail: Optional[str] = None
    duration: Optional[float] = None
    formats: list[FormatItem]
    playlist_entries: list[PlaylistEntry] = []
