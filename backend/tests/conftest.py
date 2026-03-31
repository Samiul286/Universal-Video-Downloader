import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

# Import app after patching so config uses test paths
DB_PATH = Path(tempfile.gettempdir()) / "test_downloader.db"


@pytest.fixture
def temp_download_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def app():
    with patch.dict("os.environ", {"DB_PATH": str(DB_PATH)}, clear=False):
        from main import app
        return app


@pytest.fixture
async def client(app):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
