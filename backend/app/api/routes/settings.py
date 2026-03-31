import logging

from fastapi import APIRouter

from app.database.repositories import get_all_settings, set_all_settings
from app.database.session import get_connection
from app.schemas.common import SettingsResponse, SettingsUpdate

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/settings", response_model=SettingsResponse)
async def get_settings():
    logger.debug("[DEBUG] GET /api/settings")
    conn = await get_connection()
    try:
        data = await get_all_settings(conn)
        logger.debug("[DEBUG] GET /api/settings OK keys=%s", list(data.keys()))
        return SettingsResponse(settings=data)
    finally:
        await conn.close()


@router.put("/settings", response_model=SettingsResponse)
async def put_settings(req: SettingsUpdate):
    logger.info("[DEBUG] PUT /api/settings settings=%s", req.settings)
    conn = await get_connection()
    try:
        await set_all_settings(conn, req.settings)
        data = await get_all_settings(conn)
        return SettingsResponse(settings=data)
    finally:
        await conn.close()
