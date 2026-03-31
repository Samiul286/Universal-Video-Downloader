import logging
from pathlib import Path

from fastapi import APIRouter, Body, HTTPException

from app.core.config import get_effective_download_path

logger = logging.getLogger(__name__)
from app.database.repositories import get_all_settings, set_setting
from app.database.session import get_connection
from app.downloader import manager
from app.schemas.common import DownloadItem
from app.schemas.download import DownloadRequest, DownloadResponse, RemoveDownloadsRequest

router = APIRouter()


@router.post("/download", response_model=DownloadResponse)
async def create_download(req: DownloadRequest):
    logger.info("[DEBUG] POST /api/download request url=%s format_id=%s download_path=%s", req.url, req.format_id, req.download_path)
    conn = await get_connection()
    try:
        settings_map = await get_all_settings(conn)
        settings_path = settings_map.get("download_path")
        effective = get_effective_download_path(request_path=req.download_path, settings_path=settings_path)
        logger.info("[DEBUG] POST /api/download effective path: request_path=%s settings_path=%s effective=%s", req.download_path, settings_path, effective)
        if effective is None:
            logger.warning("[DEBUG] POST /api/download no valid download path (503)")
            raise HTTPException(
                status_code=503,
                detail="no_valid_download_path",
            )
        effective_str = str(effective)
        if req.download_path and Path(req.download_path).resolve().is_dir():
            await set_setting(conn, "download_path", req.download_path)
        job_id = await manager.create_job(
            url=str(req.url),
            title=req.title,
            format_id=req.format_id,
            output_path=effective_str,
            output_template=req.output_template,
            cookies=req.cookies,
            thumbnail=req.thumbnail,
        )
        logger.info("[DEBUG] POST /api/download created job_id=%s output_path=%s", job_id, effective_str)
        return DownloadResponse(job_id=job_id)
    except ValueError as e:
        logger.warning("[DEBUG] POST /api/download ValueError: %s", e)
        if str(e) == "no_valid_download_path":
            raise HTTPException(status_code=503, detail="no_valid_download_path")
        if "disk space" in str(e).lower():
            raise HTTPException(status_code=507, detail=str(e))
        if "Queue full" in str(e):
            raise HTTPException(status_code=503, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await conn.close()


@router.get("/downloads", response_model=list[DownloadItem])
async def list_downloads():
    logger.debug("[DEBUG] GET /api/downloads")
    jobs = await manager.list_jobs()
    logger.debug("[DEBUG] GET /api/downloads count=%s", len(jobs))
    return [
        DownloadItem(
            id=j["id"],
            url=j["url"],
            title=j.get("title"),
            status=j["status"],
            progress=j.get("progress") or 0,
            filepath=j.get("filepath"),
            format_id=j.get("format_id"),
            error_message=j.get("error_message"),
            thumbnail=j.get("thumbnail"),
            created_at=j["created_at"],
            updated_at=j["updated_at"],
        )
        for j in jobs
    ]


@router.delete("/cancel/{job_id}")
async def cancel_download(job_id: str):
    logger.info("[DEBUG] DELETE /api/cancel/%s", job_id)
    ok = await manager.cancel_job(job_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"status": "cancelled"}


@router.delete("/downloads/{job_id}")
async def remove_download(job_id: str):
    logger.info("[DEBUG] DELETE /api/downloads/%s", job_id)
    ok = await manager.remove_job(job_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"status": "removed"}


@router.delete("/downloads")
async def remove_downloads(body: RemoveDownloadsRequest | None = Body(None)):
    job_ids = (body and body.job_ids) or []
    logger.info("[DEBUG] DELETE /api/downloads body job_ids=%s", job_ids)
    removed = await manager.remove_jobs(job_ids)
    return {"removed": removed}


@router.post("/pause/{job_id}")
async def pause_download(job_id: str):
    logger.info("[DEBUG] POST /api/pause/%s", job_id)
    await manager.pause_job(job_id)
    return {"status": "paused"}


@router.post("/resume/{job_id}")
async def resume_download(job_id: str):
    logger.info("[DEBUG] POST /api/resume/%s", job_id)
    await manager.resume_job(job_id)
    return {"status": "resumed"}


@router.post("/retry/{job_id}")
async def retry_download(job_id: str):
    logger.info("[DEBUG] POST /api/retry/%s", job_id)
    ok = await manager.retry_job(job_id)
    if not ok:
        raise HTTPException(status_code=400, detail="Job cannot be retried")
    return {"status": "retried"}
