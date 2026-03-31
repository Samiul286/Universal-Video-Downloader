import asyncio
import json
import logging
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.downloader.manager import set_progress_callback
from app.downloader.sources import ProgressInfo

router = APIRouter()
logger = logging.getLogger(__name__)

_connections: list[tuple[WebSocket, Optional[str]]] = []
_lock = asyncio.Lock()


async def _broadcast(job_id: str, info: ProgressInfo):
    msg = {"job_id": job_id, "percent": info.percent, "speed": info.speed, "eta": info.eta, "status": info.status}
    payload = json.dumps(msg)
    logger.debug("[DEBUG] ws broadcast job_id=%s percent=%s connections=%s", job_id, info.percent, len(_connections))
    async with _lock:
        dead = []
        for ws, filter_job in _connections:
            if filter_job is not None and filter_job != job_id:
                continue
            try:
                await ws.send_text(payload)
            except Exception:
                dead.append((ws, filter_job))
        for x in dead:
            _connections.remove(x)


def _progress_cb(job_id: str, info: ProgressInfo):
    asyncio.create_task(_broadcast(job_id, info))


def register_progress_callback() -> None:
    from app.downloader.manager import set_progress_callback
    set_progress_callback(_progress_cb)


@router.websocket("/ws/progress")
async def progress_ws(websocket: WebSocket, job_id: Optional[str] = None):
    await websocket.accept()
    async with _lock:
        _connections.append((websocket, job_id))
    logger.info("[DEBUG] ws progress_ws connected job_id=%s total_connections=%s", job_id, len(_connections))
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.debug("[DEBUG] ws progress_ws disconnected job_id=%s", job_id)
    finally:
        async with _lock:
            _connections[:] = [(w, j) for w, j in _connections if w != websocket]
