import logging
import shutil
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def get_free_bytes(path: Path) -> int:
    path.mkdir(parents=True, exist_ok=True)
    return shutil.disk_usage(str(path)).free


def has_enough_space(path: Path, estimated_bytes: Optional[int] = None, min_free_bytes: int = 50 * 1024 * 1024) -> bool:
    free = get_free_bytes(path)
    ok = (free >= estimated_bytes + min_free_bytes) if estimated_bytes is not None else (free >= min_free_bytes)
    logger.info("[DEBUG] has_enough_space path=%s estimated=%s free=%s min_free=%s ok=%s", path, estimated_bytes, free, min_free_bytes, ok)
    if estimated_bytes is not None:
        return free >= estimated_bytes + min_free_bytes
    return free >= min_free_bytes
