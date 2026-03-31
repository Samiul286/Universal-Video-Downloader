from pydantic import BaseModel
from typing import Optional


class DownloadItem(BaseModel):
    id: str
    url: str
    title: Optional[str] = None
    status: str
    progress: float = 0
    filepath: Optional[str] = None
    format_id: Optional[str] = None
    error_message: Optional[str] = None  # reason when status=failed
    thumbnail: Optional[str] = None  # video thumbnail URL for list UI
    created_at: str
    updated_at: str


class SettingsResponse(BaseModel):
    settings: dict[str, str]


class SettingsUpdate(BaseModel):
    settings: dict[str, str]
