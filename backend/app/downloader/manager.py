from __future__ import annotations

import asyncio
import logging
import time
import uuid
from pathlib import Path
from typing import Callable, Optional

from app.core.config import settings
from app.core.constants import JobStatus
from app.database.repositories import delete_download, get_download, insert_download, list_downloads, update_download
from app.database.session import get_connection, init_db
from app.downloader.queue import DownloadQueue
from app.downloader.sources import ProgressInfo
from app.downloader.ytdlp_wrapper import YtDlpSource
from app.services.disk import has_enough_space

logger = logging.getLogger(__name__)

_source = YtDlpSource()
_queue = DownloadQueue()
_running: dict[str, asyncio.Task] = {}
_paused: set[str] = set()
_progress_callback: Optional[Callable[[str, ProgressInfo], None]] = None
_progress_last: dict[str, float] = {}
_PROGRESS_THROTTLE_S = 0.25


def set_progress_callback(cb: Callable[[str, ProgressInfo], None]) -> None:
    global _progress_callback
    _progress_callback = cb


async def _update_progress(job_id: str, percent: float) -> None:
    """Persist progress to DB so GET /api/downloads returns up-to-date progress."""
    conn = await get_connection()
    try:
        await update_download(conn, job_id, progress=percent)
    finally:
        await conn.close()


async def _run_download(job_id: str) -> None:
    logger.info("[DEBUG] _run_download start job_id=%s", job_id)
    conn = await get_connection()
    try:
        row = await get_download(conn, job_id)
        if not row or row["status"] not in (JobStatus.QUEUED.value, JobStatus.DOWNLOADING.value):
            logger.debug("[DEBUG] _run_download skip job_id=%s (no row or wrong status)", job_id)
            return
        url = row["url"]
        format_id = row["format_id"]
        out_dir = row["output_path"]
        job_cookies = row.get("cookies")
        logger.info("[DEBUG] _run_download job_id=%s url=%s format_id=%s out_dir=%s", job_id, url, format_id, out_dir)
        if not out_dir:
            logger.warning("[DEBUG] _run_download job_id=%s no out_dir, marking failed", job_id)
            await update_download(conn, job_id, status=JobStatus.FAILED, error_message="No output directory")
            return
        if isinstance(out_dir, Path):
            out_dir = str(out_dir)
        Path(out_dir).mkdir(parents=True, exist_ok=True)

        # Progress hook runs inside run_in_executor (worker thread); schedule DB update and broadcast on main loop (throttled)
        loop = asyncio.get_running_loop()

        def progress_cb(info: ProgressInfo):
            def maybe_update():
                now = time.monotonic()
                last = _progress_last.get(job_id, 0)
                if info.percent >= 100 or (now - last) >= _PROGRESS_THROTTLE_S:
                    _progress_last[job_id] = now
                    asyncio.create_task(_update_progress(job_id, info.percent))
                    if _progress_callback:
                        _progress_callback(job_id, info)

            loop.call_soon_threadsafe(maybe_update)

        await update_download(conn, job_id, status=JobStatus.DOWNLOADING)
        try:
            filepath = await _source.download(url, out_dir, format_id=format_id, progress_callback=progress_cb, cookies=job_cookies)
            if filepath:
                filepath = str(Path(filepath).resolve())
            if not filepath or not Path(filepath).exists():
                msg = f"Download reported path that does not exist: {filepath}"
                logger.warning("[DEBUG] _run_download job_id=%s path missing: %s", job_id, filepath)
                await update_download(conn, job_id, status=JobStatus.FAILED, progress=0, error_message=msg)
            else:
                logger.info("[DEBUG] _run_download job_id=%s completed filepath=%s", job_id, filepath)
                await update_download(conn, job_id, status=JobStatus.COMPLETED, progress=100.0, filepath=filepath)
        except Exception as e:
            err_msg = str(e)
            logger.exception("[DEBUG] _run_download job_id=%s failed: %s", job_id, e)
            await update_download(conn, job_id, status=JobStatus.FAILED, error_message=err_msg)
    finally:
        await conn.close()
        _running.pop(job_id, None)
        _progress_last.pop(job_id, None)
        await _maybe_start_next()


async def _worker_loop() -> None:
    while True:
        job_id = await _queue.dequeue()
        if job_id is None:
            await asyncio.sleep(0.5)
            continue
        if job_id in _paused:
            await _queue.enqueue(job_id)
            await asyncio.sleep(0.5)
            continue
        _running[job_id] = asyncio.create_task(_run_download(job_id))
        if len(_running) >= settings.MAX_CONCURRENT:
            await asyncio.sleep(0.2)


async def _maybe_start_next() -> None:
    if len(_running) >= settings.MAX_CONCURRENT:
        return
    job_id = await _queue.dequeue()
    if job_id and job_id not in _paused:
        _running[job_id] = asyncio.create_task(_run_download(job_id))


async def start_manager() -> None:
    conn = await get_connection()
    try:
        await init_db(conn)
    finally:
        await conn.close()
    asyncio.create_task(_worker_loop())


async def create_job(
    url: str,
    title: Optional[str] = None,
    format_id: Optional[str] = None,
    output_path: Optional[str] = None,
    output_template: Optional[str] = None,
    estimated_bytes: Optional[int] = None,
    cookies: Optional[str] = None,
    thumbnail: Optional[str] = None,
) -> str:
    """Create a download job. output_path (effective download folder) must be set by the caller (route)."""
    logger.info("[DEBUG] create_job url=%s format_id=%s output_path=%s", url, format_id, output_path)
    if not output_path:
        logger.warning("[DEBUG] create_job rejected: no output_path")
        raise ValueError("no_valid_download_path")
    path = Path(output_path)
    path.mkdir(parents=True, exist_ok=True)
    if not has_enough_space(path, estimated_bytes):
        logger.warning("[DEBUG] create_job rejected: insufficient disk space")
        raise ValueError("Insufficient disk space")
    job_id = str(uuid.uuid4())
    conn = await get_connection()
    try:
        await insert_download(
            conn, job_id, url, title=title, status=JobStatus.QUEUED,
            format_id=format_id, output_path=output_path, output_template=output_template,
            cookies=cookies, thumbnail=thumbnail,
        )
        ok = await _queue.enqueue(job_id)
        if not ok:
            logger.warning("[DEBUG] create_job queue full, marking job %s failed", job_id)
            await update_download(conn, job_id, status=JobStatus.FAILED)
            raise ValueError("Queue full")
    finally:
        await conn.close()
    logger.info("[DEBUG] create_job enqueued job_id=%s", job_id)
    await _maybe_start_next()
    return job_id


async def get_job(job_id: str) -> Optional[dict]:
    conn = await get_connection()
    try:
        return await get_download(conn, job_id)
    finally:
        await conn.close()


async def list_jobs() -> list[dict]:
    conn = await get_connection()
    try:
        rows = await list_downloads(conn)
        logger.debug("[DEBUG] list_jobs count=%s", len(rows))
        return rows
    finally:
        await conn.close()


async def cancel_job(job_id: str) -> bool:
    logger.info("[DEBUG] cancel_job job_id=%s", job_id)
    if job_id in _running:
        _running[job_id].cancel()
    _queue.remove(job_id)
    _paused.discard(job_id)
    conn = await get_connection()
    try:
        await update_download(conn, job_id, status=JobStatus.CANCELLED)
        return True
    finally:
        await conn.close()


async def pause_job(job_id: str) -> bool:
    logger.info("[DEBUG] pause_job job_id=%s", job_id)
    _paused.add(job_id)
    conn = await get_connection()
    try:
        await update_download(conn, job_id, status=JobStatus.PAUSED)
        return True
    finally:
        await conn.close()


async def resume_job(job_id: str) -> bool:
    logger.info("[DEBUG] resume_job job_id=%s", job_id)
    _paused.discard(job_id)
    conn = await get_connection()
    try:
        row = await get_download(conn, job_id)
        if row and row["status"] == JobStatus.PAUSED.value:
            await update_download(conn, job_id, status=JobStatus.QUEUED)
            await _queue.enqueue(job_id)
            await _maybe_start_next()
        return True
    finally:
        await conn.close()


async def retry_job(job_id: str) -> bool:
    logger.info("[DEBUG] retry_job job_id=%s", job_id)
    conn = await get_connection()
    try:
        row = await get_download(conn, job_id)
        if not row or row["status"] != JobStatus.FAILED.value:
            logger.warning("[DEBUG] retry_job job_id=%s not retriable status=%s", job_id, row["status"] if row else None)
            return False
        await update_download(conn, job_id, status=JobStatus.QUEUED)
        await _queue.enqueue(job_id)
        await _maybe_start_next()
        return True
    finally:
        await conn.close()


async def remove_job(job_id: str) -> bool:
    """Remove a job from queue/workers and delete from DB. Cancels if running."""
    logger.info("[DEBUG] remove_job job_id=%s", job_id)
    if job_id in _running:
        _running[job_id].cancel()
    _queue.remove(job_id)
    _paused.discard(job_id)
    conn = await get_connection()
    try:
        ok = await delete_download(conn, job_id)
        logger.debug("[DEBUG] remove_job job_id=%s deleted=%s", job_id, ok)
        return ok
    finally:
        await conn.close()


async def remove_jobs(job_ids: list[str]) -> int:
    """Remove multiple jobs. If job_ids is empty, remove all. Returns count removed."""
    if not job_ids:
        conn = await get_connection()
        try:
            rows = await list_downloads(conn)
            job_ids = [r["id"] for r in rows]
        finally:
            await conn.close()
    removed = 0
    for jid in job_ids:
        if await remove_job(jid):
            removed += 1
    return removed
