"""
BE-I3b: POST /api/download no valid path → 503 and detail no_valid_download_path.
        When request includes valid download_path, persist it and accept job.
BE-I10: GET /ready returns 503 when no valid download folder; 200 when ready.
"""
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def test_db_path():
    return Path(tempfile.gettempdir()) / "test_download_ready.db"


@pytest.fixture
def app_with_test_db(test_db_path):
    with patch.dict("os.environ", {"DB_PATH": str(test_db_path)}, clear=False):
        from main import app
        return app


@pytest.mark.asyncio
async def test_ready_503_when_no_valid_download_folder(app_with_test_db):
    """BE-I10: GET /ready returns 503 when effective download folder is not set or not found."""
    with patch("app.api.routes.health.get_effective_download_path", return_value=None):
        async with AsyncClient(
            transport=ASGITransport(app=app_with_test_db),
            base_url="http://test",
        ) as client:
            r = await client.get("/ready")
            assert r.status_code == 503
            data = r.json()
            assert data.get("reason") == "no_valid_download_path"


@pytest.mark.asyncio
async def test_ready_200_when_valid_download_folder(app_with_test_db):
    """BE-I10: GET /ready returns 200 when DB and effective download folder are ready."""
    with patch("app.api.routes.health.get_effective_download_path") as m:
        m.return_value = Path(tempfile.gettempdir())
        async with AsyncClient(
            transport=ASGITransport(app=app_with_test_db),
            base_url="http://test",
        ) as client:
            r = await client.get("/ready")
            assert r.status_code == 200
            assert r.json().get("status") == "ready"


@pytest.mark.asyncio
async def test_download_503_when_no_valid_path(app_with_test_db):
    """BE-I3b: POST /api/download with no valid save folder returns 503 and no_valid_download_path."""
    with patch("app.api.routes.downloads.get_effective_download_path", return_value=None):
        async with AsyncClient(
            transport=ASGITransport(app=app_with_test_db),
            base_url="http://test",
        ) as client:
            r = await client.post(
                "/api/download",
                json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
            )
            assert r.status_code == 503
            assert r.json().get("detail") == "no_valid_download_path"


@pytest.mark.asyncio
async def test_download_accepts_valid_download_path_and_persists(app_with_test_db):
    """BE-I3b: When request includes valid download_path, persist it and accept job."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("app.api.routes.downloads.get_effective_download_path") as m:
            m.return_value = Path(tmpdir)
            async with AsyncClient(
                transport=ASGITransport(app=app_with_test_db),
                base_url="http://test",
            ) as client:
                r = await client.post(
                    "/api/download",
                    json={
                        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                        "download_path": tmpdir,
                    },
                )
                assert r.status_code == 200
                data = r.json()
                assert "job_id" in data
                # Settings should have been updated with download_path
                r2 = await client.get("/api/settings")
                assert r2.status_code == 200
                settings = r2.json().get("settings", {})
                assert settings.get("download_path") == tmpdir
