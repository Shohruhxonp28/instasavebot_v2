"""
Database connection and schema setup (SQLite via aiosqlite).
"""
import aiosqlite
from bot.config import DB_PATH

_connection: aiosqlite.Connection | None = None


async def get_connection() -> aiosqlite.Connection:
    """Return the shared database connection, creating it if needed."""
    global _connection
    if _connection is None:
        _connection = await aiosqlite.connect(DB_PATH)
        _connection.row_factory = aiosqlite.Row
        await _connection.execute("PRAGMA foreign_keys = ON;")
    return _connection


async def init_db() -> None:
    """Create all required tables if they don't exist yet."""
    db = await get_connection()

    await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            language TEXT DEFAULT 'en',
            is_blocked INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            last_active TEXT DEFAULT (datetime('now'))
        );
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS required_channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id TEXT NOT NULL,
            username TEXT,
            title TEXT,
            active INTEGER DEFAULT 1
        );
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        );
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS downloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            platform TEXT,
            success INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now'))
        );
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS recognitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            success INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        );
    """)

    await db.commit()


async def close_db() -> None:
    global _connection
    if _connection is not None:
        await _connection.close()
        _connection = None
