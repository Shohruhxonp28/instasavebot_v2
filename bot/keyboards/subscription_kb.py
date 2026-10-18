from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


from bot.services.i18n import t


def subscription_keyboard(channels, lang: str = "uz") -> InlineKeyboardMarkup:
    """Build a keyboard with a button per required channel plus a check button."""
    builder = InlineKeyboardBuilder()
    for ch in channels:
        link_username = ch["username"] or ch["channel_id"]
        url = f"https://t.me/{link_username.lstrip('@')}"
        title = ch["title"] or link_username
        builder.row(InlineKeyboardButton(text=f"📺 {title}", url=url))
    builder.row(InlineKeyboardButton(text=t("check_sub_btn", lang), callback_data="check_subscription"))
    return builder.as_markup()
