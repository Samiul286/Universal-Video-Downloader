from __future__ import annotations

import logging
import aiosqlite
from datetime import datetime, timezone
from typing import Any, Optional

from app.core.constants import JobStatus

logger = logging.getLogger(__name__)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _status_value(s: Any) -> str:
    return getattr(s, "value", s) if s is not None else s


async def insert_download(
    conn: aiosqlite.Connection,
    id: str,
    url: str,
    title: Optional[str] = None,
    status: str = JobStatus.QUEUED,
    format_id: Optional[str] = None,
    output_path: Optional[str] = None,
    output_template: Optional[str] = None,
    cookies: Optional[str] = None,
    thumbnail: Optional[str] = None,
) -> None:
    logger.info("[DEBUG] insert_download id=%s url=%s status=%s output_path=%s", id, url, _status_value(status), output_path)
    now = _now()
    await conn.execute(
        """INSERT INTO downloads (id, url, title, status, progress, filepath, format_id, output_path, output_template, cookies, thumbnail, created_at, updated_at)
           VALUES (?, ?, ?, ?, 0, NULL, ?, ?, ?, ?, ?, ?, ?)""",
        (id, url, title or "", _status_value(status), format_id, output_path, output_template, cookies, thumbnail, now, now),
    )
    await conn.commit()


async def update_download(
    conn: aiosqlite.Connection,
    id: str,
    *,
    status: Optional[str] = None,
    progress: Optional[float] = None,
    filepath: Optional[str] = None,
    error_message: Optional[str] = None,
) -> None:
    logger.debug("[DEBUG] update_download id=%s status=%s progress=%s filepath=%s error_message=%s", id, status, progress, filepath, bool(error_message))
    now = _now()
    updates = ["updated_at = ?"]
    params: list[Any] = [now]
    if status is not None:
        updates.append("status = ?")
        params.append(_status_value(status))
    if progress is not None:
        updates.append("progress = ?")
        params.append(progress)
    if filepath is not None:
        updates.append("filepath = ?")
        params.append(filepath)
    if error_message is not None:
        updates.append("error_message = ?")
        params.append(error_message)
    params.append(id)
    await conn.execute(f"UPDATE downloads SET {', '.join(updates)} WHERE id = ?", params)
    await conn.commit()


async def get_download(conn: aiosqlite.Connection, id: str) -> Optional[dict]:
    cursor = await conn.execute(
        "SELECT id, url, title, status, progress, filepath, format_id, output_path, output_template, error_message, cookies, thumbnail, created_at, updated_at FROM downloads WHERE id = ?",
        (id,),
    )
    row = await cursor.fetchone()
    out = dict(row) if row else None
    logger.debug("[DEBUG] get_download id=%s found=%s", id, out is not None)
    return out


async def list_downloads(conn: aiosqlite.Connection) -> list[dict]:
    cursor = await conn.execute(
        "SELECT id, url, title, status, progress, filepath, format_id, output_path, output_template, error_message, cookies, thumbnail, created_at, updated_at FROM downloads ORDER BY created_at DESC"
    )
    rows = [dict(r) for r in await cursor.fetchall()]
    logger.debug("[DEBUG] list_downloads count=%s", len(rows))
    return rows


async def delete_download(conn: aiosqlite.Connection, id: str) -> bool:
    cursor = await conn.execute("DELETE FROM downloads WHERE id = ?", (id,))
    await conn.commit()
    ok = cursor.rowcount > 0
    logger.info("[DEBUG] delete_download id=%s deleted=%s", id, ok)
    return ok


async def get_setting(conn: aiosqlite.Connection, key: str) -> Optional[str]:
    cursor = await conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = await cursor.fetchone()
    return row[0] if row else None


async def set_setting(conn: aiosqlite.Connection, key: str, value: str) -> None:
    logger.info("[DEBUG] set_setting key=%s value=%s", key, value)
    await conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )
    await conn.commit()


async def get_all_settings(conn: aiosqlite.Connection) -> dict[str, str]:
    cursor = await conn.execute("SELECT key, value FROM settings")
    data = {r[0]: r[1] for r in await cursor.fetchall()}
    logger.debug("[DEBUG] get_all_settings keys=%s", list(data.keys()))
    return data


async def set_all_settings(conn: aiosqlite.Connection, data: dict[str, str]) -> None:
    for k, v in data.items():
        await set_setting(conn, k, str(v))
