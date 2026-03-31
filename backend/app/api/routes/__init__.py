from fastapi import APIRouter

from .downloads import router as downloads_router
from .extract import router as extract_router
from .health import router as health_router
from .settings import router as settings_router

api_router = APIRouter(prefix="/api", tags=["api"])
api_router.include_router(extract_router, prefix="", tags=["extract"])
api_router.include_router(downloads_router, prefix="", tags=["downloads"])
api_router.include_router(settings_router, prefix="", tags=["settings"])

# Health/ready at root level
health_router_instance = health_router
