import asyncio
import logging
from collections import deque
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class DownloadQueue:
    def __init__(self, max_size: Optional[int] = None):
        self._max_size = max_size or settings.QUEUE_MAX_SIZE
        self._queue: deque[str] = deque()
        self._lock = asyncio.Lock()

    @property
    def size(self) -> int:
        return len(self._queue)

    async def enqueue(self, job_id: str) -> bool:
        async with self._lock:
            if len(self._queue) >= self._max_size:
                logger.warning("[DEBUG] queue enqueue rejected (full) job_id=%s size=%s max=%s", job_id, len(self._queue), self._max_size)
                return False
            self._queue.append(job_id)
            logger.info("[DEBUG] queue enqueue job_id=%s size=%s", job_id, len(self._queue))
            return True

    async def dequeue(self) -> Optional[str]:
        async with self._lock:
            job_id = self._queue.popleft() if self._queue else None
            if job_id:
                logger.debug("[DEBUG] queue dequeue job_id=%s remaining=%s", job_id, len(self._queue))
            return job_id

    async def list_ids(self) -> list[str]:
        async with self._lock:
            return list(self._queue)

    def remove(self, job_id: str) -> bool:
        try:
            self._queue.remove(job_id)
            logger.debug("[DEBUG] queue remove job_id=%s", job_id)
            return True
        except ValueError:
            logger.debug("[DEBUG] queue remove job_id=%s not in queue", job_id)
            return False
