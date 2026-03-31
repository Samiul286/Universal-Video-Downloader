"""BE-U1: yt-dlp wrapper extract (mocked). BE-U2: extract playlist (mocked)."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.downloader.sources import ExtractResult, FormatInfo
from app.downloader.ytdlp_wrapper import YtDlpSource


@pytest.mark.asyncio
async def test_ytdlp_extract_returns_title_formats_thumbnail_duration():
    fake_info = {
        "title": "Test Video",
        "thumbnail": "https://example.com/thumb.jpg",
        "duration": 120.0,
        "formats": [
            {"format_id": "22", "ext": "mp4", "height": 720, "filesize": 10_000_000, "vcodec": "avc", "acodec": "mp4a"},
        ],
        "entries": None,
    }

    def fake_extract(url, download=False):
        return fake_info

    with patch("yt_dlp.YoutubeDL") as mock_ydl:
        mock_ydl.return_value.__enter__.return_value.extract_info = fake_extract
        source = YtDlpSource()
        result = await source.extract("https://www.youtube.com/watch?v=abc")
    assert isinstance(result, ExtractResult)
    assert result.title == "Test Video"
    assert result.thumbnail == "https://example.com/thumb.jpg"
    assert result.duration == 120.0
    assert len(result.formats) >= 1
    assert result.formats[0].format_id == "22"


@pytest.mark.asyncio
async def test_ytdlp_extract_playlist_returns_entries():
    fake_info = {
        "title": "Playlist",
        "_type": "playlist",
        "thumbnail": None,
        "duration": None,
        "formats": [],
        "entries": [
            {"id": "e1", "title": "Entry 1", "url": "https://youtube.com/watch?v=e1"},
            {"id": "e2", "title": "Entry 2", "url": "https://youtube.com/watch?v=e2"},
        ],
    }

    def fake_extract(url, download=False):
        return fake_info

    with patch("yt_dlp.YoutubeDL") as mock_ydl:
        mock_ydl.return_value.__enter__.return_value.extract_info = fake_extract
        source = YtDlpSource()
        result = await source.extract("https://www.youtube.com/playlist?list=abc")
    assert len(result.playlist_entries) == 2
    assert result.playlist_entries[0].get("id") == "e1"
    assert result.playlist_entries[0].get("title") == "Entry 1"
    assert result.playlist_entries[1].get("url") == "https://youtube.com/watch?v=e2"
