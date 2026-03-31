import logging
import sys
from contextvars import ContextVar
from typing import Any

request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)
job_id_ctx: ContextVar[str | None] = ContextVar("job_id", default=None)


def get_log_extra() -> dict[str, Any]:
    extra: dict[str, Any] = {}
    if request_id_ctx.get():
        extra["request_id"] = request_id_ctx.get()
    if job_id_ctx.get():
        extra["job_id"] = job_id_ctx.get()
    return extra


class CorrelationFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get() or ""
        record.job_id = job_id_ctx.get() or ""
        return True


def setup_logging(level: str = "INFO") -> None:
    fmt = "%(asctime)s | %(levelname)s | %(name)s | request_id=%(request_id)s job_id=%(job_id)s | %(message)s"
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt))
    handler.addFilter(CorrelationFilter())
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)
    logging.LogRecord.request_id = ""
    logging.LogRecord.job_id = ""
