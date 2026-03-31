"""BE-U7: Config load — Pydantic config loads from env; defaults for PORT, BIND, DOWNLOAD_PATH, etc."""
import os
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.mark.parametrize("var,expected_default", [
    ("PORT", 8000),
    ("BIND", "0.0.0.0"),
    ("MAX_CONCURRENT", 2),
    ("QUEUE_MAX_SIZE", 100),
])
def test_config_defaults(var, expected_default):
    with patch.dict(os.environ, {}, clear=False):
        for k in ["PORT", "BIND", "DOWNLOAD_PATH", "DB_PATH", "MAX_CONCURRENT", "QUEUE_MAX_SIZE", "FFMPEG_PATH", "PROXY", "COOKIES_PATH"]:
            os.environ.pop(k, None)
        from app.core.config import Settings
        s = Settings()
        assert getattr(s, var) == expected_default


def test_config_optional_paths_default_none():
    with patch.dict(os.environ, {}, clear=False):
        for k in ["DOWNLOAD_PATH", "FFMPEG_PATH", "PROXY", "COOKIES_PATH"]:
            os.environ.pop(k, None)
        from app.core.config import Settings
        s = Settings()
        assert s.DOWNLOAD_PATH is None
        assert s.FFMPEG_PATH is None
        assert s.PROXY is None
        assert s.COOKIES_PATH is None


def test_get_effective_download_path_system_downloads():
    from app.core.config import get_effective_download_path
    with patch.dict(os.environ, {}, clear=False):
        for k in ["DOWNLOAD_PATH"]:
            os.environ.pop(k, None)
        # If system Downloads exists, should return it when no request/settings
        result = get_effective_download_path(request_path=None, settings_path=None)
        # May be None on CI or Path(Downloads)
        assert result is None or (result and result.is_dir())
