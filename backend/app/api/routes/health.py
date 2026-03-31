import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.config import get_effective_download_path
from app.database.repositories import get_all_settings
from app.database.session import get_connection, init_db

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/ready")
async def ready():
    logger.info("[DEBUG] GET /ready")
    try:
        conn = await get_connection()
        await init_db(conn)
        settings_map = await get_all_settings(conn)
        await conn.close()
        download_path_from_settings = settings_map.get("download_path")
        effective = get_effective_download_path(settings_path=download_path_from_settings)
        if effective is None:
            logger.warning("[DEBUG] GET /ready 503 no_valid_download_path")
            return JSONResponse(
                status_code=503,
                content={"status": "not_ready", "reason": "no_valid_download_path"},
            )
        logger.info("[DEBUG] GET /ready 200 effective=%s", effective)
    except Exception as e:
        logger.exception("[DEBUG] GET /ready 503 exception: %s", e)
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "reason": str(e)},
        )
    return {"status": "ready"}
