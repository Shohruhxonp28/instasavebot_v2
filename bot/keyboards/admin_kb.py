from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_main_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="👥 Users", callback_data="admin_users"))
    builder.row(InlineKeyboardButton(text="📊 Statistics", callback_data="admin_stats"))
    builder.row(InlineKeyboardButton(text="📢 Broadcast Message", callback_data="admin_broadcast"))
    builder.row(InlineKeyboardButton(text="📺 Required Channels", callback_data="admin_channels"))
    builder.row(InlineKeyboardButton(text="👑 Admin Settings", callback_data="admin_settings"))
    builder.row(InlineKeyboardButton(text="❌ Exit", callback_data="admin_exit"))
    return builder.as_markup()


def back_to_admin_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⬅️ Back", callback_data="admin_back"))
    return builder.as_markup()


def users_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔎 Search by ID", callback_data="users_search"))
    builder.row(InlineKeyboardButton(text="⬅️ Back", callback_data="admin_back"))
    return builder.as_markup()


def user_actions_menu(telegram_id: int, is_blocked: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if is_blocked:
        builder.row(InlineKeyboardButton(text="✅ Unblock", callback_data=f"unblock_{telegram_id}"))
    else:
        builder.row(InlineKeyboardButton(text="🚫 Block", callback_data=f"block_{telegram_id}"))
    builder.row(InlineKeyboardButton(text="⬅️ Back", callback_data="admin_users"))
    return builder.as_markup()


def broadcast_type_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📝 Text", callback_data="bctype_text"),
        InlineKeyboardButton(text="🖼 Photo", callback_data="bctype_photo"),
    )
    builder.row(
        InlineKeyboardButton(text="🎬 Video", callback_data="bctype_video"),
        InlineKeyboardButton(text="🎞 Animation", callback_data="bctype_animation"),
    )
    builder.row(InlineKeyboardButton(text="📄 Document", callback_data="bctype_document"))
    builder.row(InlineKeyboardButton(text="⬅️ Back", callback_data="admin_back"))
    return builder.as_markup()


def broadcast_confirm_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Send", callback_data="broadcast_send"),
        InlineKeyboardButton(text="❌ Cancel", callback_data="broadcast_cancel"),
    )
    return builder.as_markup()


def channels_menu(channels) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for ch in channels:
        status = "🟢" if ch["active"] else "🔴"
        title = ch["title"] or ch["username"] or ch["channel_id"]
        builder.row(
            InlineKeyboardButton(text=f"{status} {title}", callback_data=f"chinfo_{ch['id']}")
        )
    builder.row(InlineKeyboardButton(text="➕ Add channel", callback_data="channel_add"))
    builder.row(InlineKeyboardButton(text="⬅️ Back", callback_data="admin_back"))
    return builder.as_markup()


def channel_detail_menu(channel_db_id: int, active: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    toggle_text = "🔴 Disable" if active else "🟢 Enable"
    builder.row(InlineKeyboardButton(text=toggle_text, callback_data=f"chtoggle_{channel_db_id}"))
    builder.row(InlineKeyboardButton(text="🗑 Remove", callback_data=f"chremove_{channel_db_id}"))
    builder.row(InlineKeyboardButton(text="⬅️ Back", callback_data="admin_channels"))
    return builder.as_markup()
