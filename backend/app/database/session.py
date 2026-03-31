import logging
import aiosqlite
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)
DB_PATH = Path(settings.DB_PATH)


async def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = await aiosqlite.connect(str(DB_PATH))
    conn.row_factory = aiosqlite.Row
    logger.debug("[DEBUG] get_connection db=%s", DB_PATH)
    return conn


async def init_db(conn: aiosqlite.Connection) -> None:
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS downloads (
            id TEXT PRIMARY KEY,
            url TEXT NOT NULL,
            title TEXT,
            status TEXT NOT NULL,
            progress REAL DEFAULT 0,
            filepath TEXT,
            format_id TEXT,
            output_path TEXT,
            output_template TEXT,
            error_message TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    # Add columns for DBs created before they existed
    for col in ("error_message", "cookies", "thumbnail"):
        try:
            await conn.execute(f"ALTER TABLE downloads ADD COLUMN {col} TEXT")
        except Exception:
            pass
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    await conn.commit()
    logger.debug("[DEBUG] init_db tables ensured")
