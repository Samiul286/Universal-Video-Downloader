"""BE-I1 extract, BE-I2 download, BE-I3 disk, BE-I4 list, BE-I5 cancel, BE-I6 pause/resume, BE-I7 retry, BE-I8 settings, BE-I9 health."""
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def test_db_path(tmp_path):
    """Unique DB per test so jobs from other tests don't leak."""
    return tmp_path / "test_api.db"


@pytest.fixture
def app_with_db(test_db_path):
    """App with DB path patched per test so each test gets an isolated DB."""
    with patch("app.database.session.DB_PATH", test_db_path):
        from main import app
        from app.database.session import get_connection, init_db
        async def _init():
            conn = await get_connection()
            await init_db(conn)
            await conn.close()
        asyncio.run(_init())
        yield app


@pytest.mark.asyncio
async def test_health_200(app_with_db):
    """BE-I9: GET /health — 200, no dependency checks."""
    async with AsyncClient(transport=ASGITransport(app=app_with_db), base_url="http://test") as client:
        r = await client.get("/health")
        assert r.status_code == 200
        assert r.json().get("status") == "ok"


@pytest.mark.asyncio
async def test_extract_200_with_mock(app_with_db):
    """BE-I1: POST /api/extract — valid URL (mocked): 200, title, formats, thumbnail, duration."""
    from unittest.mock import AsyncMock
    from app.downloader.sources import ExtractResult, FormatInfo
    result = ExtractResult(
        title="Mocked Title",
        thumbnail="https://example.com/t.jpg",
        duration=90.0,
        formats=[FormatInfo("22", "mp4", "720p", 1000000, "avc", "mp4a")],
        playlist_entries=[],
    )
    with patch("app.api.routes.extract._source") as mock_src:
        mock_src.extract = AsyncMock(return_value=result)
        async with AsyncClient(transport=ASGITransport(app=app_with_db), base_url="http://test") as client:
            r = await client.post("/api/extract", json={"url": "https://www.youtube.com/watch?v=abc"})
            assert r.status_code == 200
            data = r.json()
            assert data["title"] == "Mocked Title"
            assert data["thumbnail"] == "https://example.com/t.jpg"
            assert data["duration"] == 90.0
            assert len(data["formats"]) == 1


@pytest.mark.asyncio
async def test_extract_invalid_url_4xx(app_with_db):
    async with AsyncClient(transport=ASGITransport(app=app_with_db), base_url="http://test") as client:
        r = await client.post("/api/extract", json={"url": "not-a-valid-url"})
        assert r.status_code == 422


@pytest.mark.asyncio
async def test_download_and_list(app_with_db):
    """BE-I2: POST /api/download valid → job id; BE-I4: GET /api/downloads returns list with id, url, title, status, progress."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("app.api.routes.downloads.get_effective_download_path") as m:
            m.return_value = Path(tmpdir)
            async with AsyncClient(transport=ASGITransport(app=app_with_db), base_url="http://test") as client:
                r = await client.post("/api/download", json={"url": "https://www.youtube.com/watch?v=xyz"})
                assert r.status_code == 200
                data = r.json()
                assert "job_id" in data
                job_id = data["job_id"]
                r2 = await client.get("/api/downloads")
                assert r2.status_code == 200
                jobs = r2.json()
                assert any(j["id"] == job_id for j in jobs)
                j = next(j for j in jobs if j["id"] == job_id)
                assert j["url"] == "https://www.youtube.com/watch?v=xyz"
                assert j["status"] in ("queued", "downloading")
                assert "progress" in j


@pytest.mark.asyncio
async def test_cancel_job(app_with_db):
    """BE-I5: DELETE /api/cancel/id — status updated."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("app.api.routes.downloads.get_effective_download_path") as m:
            m.return_value = Path(tmpdir)
            async with AsyncClient(transport=ASGITransport(app=app_with_db), base_url="http://test") as client:
                r = await client.post("/api/download", json={"url": "https://example.com/v"})
                assert r.status_code == 200
                job_id = r.json()["job_id"]
                r2 = await client.delete(f"/api/cancel/{job_id}")
                assert r2.status_code == 200
                r3 = await client.get("/api/downloads")
                jobs = [j for j in r3.json() if j["id"] == job_id]
                assert len(jobs) == 1 and jobs[0]["status"] == "cancelled"


@pytest.mark.asyncio
async def test_settings_get_put(app_with_db):
    """BE-I8: GET /api/settings, PUT /api/settings — GET reflects change."""
    async with AsyncClient(transport=ASGITransport(app=app_with_db), base_url="http://test") as client:
        r = await client.get("/api/settings")
        assert r.status_code == 200
        assert "settings" in r.json()
        r2 = await client.put("/api/settings", json={"settings": {"download_path": "C:\\Videos"}})
        assert r2.status_code == 200
        r3 = await client.get("/api/settings")
        assert r3.json()["settings"].get("download_path") == "C:\\Videos"


@pytest.mark.asyncio
async def test_download_insufficient_disk_4xx(app_with_db):
    """BE-I3: POST /api/download when disk check fails — 4xx, no job created."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("app.api.routes.downloads.get_effective_download_path") as m_path:
            m_path.return_value = Path(tmpdir)
            with patch("app.downloader.manager.has_enough_space", return_value=False):
                async with AsyncClient(transport=ASGITransport(app=app_with_db), base_url="http://test") as client:
                    r = await client.post("/api/download", json={"url": "https://example.com/v"})
                    assert r.status_code in (400, 407, 507)
                    r2 = await client.get("/api/downloads")
                    jobs = [j for j in r2.json() if j["url"] == "https://example.com/v"]
                    assert len(jobs) == 0


@pytest.mark.asyncio
async def test_retry_failed_job(app_with_db):
    """BE-I7: POST /api/retry/id — failed job can be retried; new attempt enqueued."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("app.api.routes.downloads.get_effective_download_path") as m:
            m.return_value = Path(tmpdir)
            async with AsyncClient(transport=ASGITransport(app=app_with_db), base_url="http://test") as client:
                r = await client.post("/api/download", json={"url": "https://example.com/v2"})
                assert r.status_code == 200
                job_id = r.json()["job_id"]
                # Mark as failed in DB (manager would do this on error)
                from app.database.session import get_connection
                from app.database.repositories import update_download
                from app.core.constants import JobStatus
                conn = await get_connection()
                await update_download(conn, job_id, status=JobStatus.FAILED.value)
                await conn.close()
                r2 = await client.post(f"/api/retry/{job_id}")
                assert r2.status_code == 200
                r3 = await client.get("/api/downloads")
                j = next((x for x in r3.json() if x["id"] == job_id), None)
                assert j is not None and j["status"] in ("queued", "downloading")
