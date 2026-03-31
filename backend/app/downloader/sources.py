from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Optional


@dataclass
class FormatInfo:
    format_id: str
    ext: Optional[str]
    resolution: Optional[str]
    filesize: Optional[int]
    vcodec: Optional[str]
    acodec: Optional[str]


@dataclass
class ExtractResult:
    title: str
    thumbnail: Optional[str]
    duration: Optional[float]
    formats: list[FormatInfo]
    playlist_entries: list[dict]


@dataclass
class ProgressInfo:
    percent: float
    speed: Optional[float]
    eta: Optional[float]
    status: str


class VideoSource(ABC):
    @abstractmethod
    async def extract(self, url: str) -> ExtractResult:
        ...

    @abstractmethod
    async def download(
        self,
        url: str,
        output_path: str,
        format_id: Optional[str] = None,
        progress_callback: Optional[Callable[[ProgressInfo], None]] = None,
    ) -> str:
        ...
