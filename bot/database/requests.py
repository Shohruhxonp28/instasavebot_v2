"""
All database queries live here. Handlers/services call these functions
instead of writing raw SQL, keeping the rest of the codebase clean.
"""
from bot.database.db import get_connection


# ---------- Users ----------

async def add_user(telegram_id: int, username: str | None, first_name: str | None) -> None:
    db = await get_connection()
    await db.execute(
        """
        INSERT INTO users (telegram_id, username, first_name)
        VALUES (?, ?, ?)
        ON CONFLICT(telegram_id) DO UPDATE SET
            username = excluded.username,
            first_name = excluded.first_name,
            last_active = datetime('now')
        """,
        (telegram_id, username, first_name),
    )
    await db.commit()


async def touch_user(telegram_id: int) -> None:
    """Update last_active timestamp for a user."""
    db = await get_connection()
    await db.execute(
        "UPDATE users SET last_active = datetime('now') WHERE telegram_id = ?",
        (telegram_id,),
    )
    await db.commit()


async def get_user(telegram_id: int):
    db = await get_connection()
    cursor = await db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    return await cursor.fetchone()


async def is_user_blocked(telegram_id: int) -> bool:
    user = await get_user(telegram_id)
    return bool(user["is_blocked"]) if user else False


async def set_user_blocked(telegram_id: int, blocked: bool) -> None:
    db = await get_connection()
    await db.execute(
        "UPDATE users SET is_blocked = ? WHERE telegram_id = ?",
        (1 if blocked else 0, telegram_id),
    )
    await db.commit()


async def get_all_user_ids() -> list[int]:
    db = await get_connection()
    cursor = await db.execute("SELECT telegram_id FROM users")
    rows = await cursor.fetchall()
    return [row["telegram_id"] for row in rows]


async def count_total_users() -> int:
    db = await get_connection()
    cursor = await db.execute("SELECT COUNT(*) AS cnt FROM users")
    row = await cursor.fetchone()
    return row["cnt"]


async def count_active_users_today() -> int:
    db = await get_connection()
    cursor = await db.execute(
        "SELECT COUNT(*) AS cnt FROM users WHERE date(last_active) = date('now')"
    )
    row = await cursor.fetchone()
    return row["cnt"]


# ---------- Required Channels ----------

async def add_required_channel(channel_id: str, username: str | None, title: str | None) -> None:
    db = await get_connection()
    await db.execute(
        "INSERT INTO required_channels (channel_id, username, title, active) VALUES (?, ?, ?, 1)",
        (channel_id, username, title),
    )
    await db.commit()


async def remove_required_channel(channel_db_id: int) -> None:
    db = await get_connection()
    await db.execute("DELETE FROM required_channels WHERE id = ?", (channel_db_id,))
    await db.commit()


async def toggle_required_channel(channel_db_id: int) -> None:
    db = await get_connection()
    await db.execute(
        "UPDATE required_channels SET active = 1 - active WHERE id = ?",
        (channel_db_id,),
    )
    await db.commit()


async def get_all_required_channels():
    db = await get_connection()
    cursor = await db.execute("SELECT * FROM required_channels ORDER BY id")
    return await cursor.fetchall()


async def get_active_required_channels():
    db = await get_connection()
    cursor = await db.execute("SELECT * FROM required_channels WHERE active = 1 ORDER BY id")
    return await cursor.fetchall()


async def get_required_channel(channel_db_id: int):
    db = await get_connection()
    cursor = await db.execute("SELECT * FROM required_channels WHERE id = ?", (channel_db_id,))
    return await cursor.fetchone()


# ---------- Settings ----------

async def get_setting(key: str, default: str | None = None) -> str | None:
    db = await get_connection()
    cursor = await db.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = await cursor.fetchone()
    return row["value"] if row else default


async def set_setting(key: str, value: str) -> None:
    db = await get_connection()
    await db.execute(
        """
        INSERT INTO settings (key, value) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """,
        (key, value),
    )
    await db.commit()


# ---------- Stats: downloads & recognitions ----------

async def log_download(telegram_id: int, platform: str, success: bool) -> None:
    db = await get_connection()
    await db.execute(
        "INSERT INTO downloads (telegram_id, platform, success) VALUES (?, ?, ?)",
        (telegram_id, platform, 1 if success else 0),
    )
    await db.commit()


async def log_recognition(telegram_id: int, success: bool) -> None:
    db = await get_connection()
    await db.execute(
        "INSERT INTO recognitions (telegram_id, success) VALUES (?, ?)",
        (telegram_id, 1 if success else 0),
    )
    await db.commit()


async def get_stats() -> dict:
    db = await get_connection()

    total_users = await count_total_users()
    active_today = await count_active_users_today()

    cursor = await db.execute("SELECT COUNT(*) AS cnt FROM downloads WHERE success = 1")
    total_downloads = (await cursor.fetchone())["cnt"]

    async def platform_count(platform: str) -> int:
        cur = await db.execute(
            "SELECT COUNT(*) AS cnt FROM downloads WHERE success = 1 AND platform = ?",
            (platform,),
        )
        return (await cur.fetchone())["cnt"]

    tiktok = await platform_count("TikTok")
    instagram = await platform_count("Instagram")
    youtube = await platform_count("YouTube")

    cursor = await db.execute("SELECT COUNT(*) AS cnt FROM recognitions WHERE success = 1")
    recognized = (await cursor.fetchone())["cnt"]

    cursor = await db.execute("SELECT COUNT(*) AS cnt FROM recognitions WHERE success = 0")
    failed_recognitions = (await cursor.fetchone())["cnt"]

    return {
        "total_users": total_users,
        "active_today": active_today,
        "total_downloads": total_downloads,
        "tiktok": tiktok,
        "instagram": instagram,
        "youtube": youtube,
        "recognized": recognized,
        "failed_recognitions": failed_recognitions,
    }
