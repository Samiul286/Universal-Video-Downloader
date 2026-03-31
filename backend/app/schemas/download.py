from pydantic import BaseModel, HttpUrl
from typing import Optional, List


class DownloadRequest(BaseModel):
    url: HttpUrl
    title: Optional[str] = None  # Video title (from extract); shown in downloads list
    format_id: Optional[str] = None
    output_path: Optional[str] = None
    output_template: Optional[str] = None
    download_path: Optional[str] = None  # User-chosen folder from "Choose folder to save"; persisted and used for this and future downloads
    cookies: Optional[str] = None  # Netscape-format cookies (per-user); stored with job and used for this download
    thumbnail: Optional[str] = None  # Video thumbnail URL (e.g. from extract); shown in downloads list


class DownloadResponse(BaseModel):
    job_id: str


class RemoveDownloadsRequest(BaseModel):
    job_ids: List[str] = []  # empty = remove all
