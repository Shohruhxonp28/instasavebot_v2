from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from bot.utils.filters import IsAdmin
from bot.config import ADMIN_IDS
from bot.database.requests import get_setting, set_setting
from bot.keyboards.admin_kb import back_to_admin_menu

router = Router()
router.callback_query.filter(IsAdmin())


def _settings_keyboard(force_sub_enabled: bool):
    builder = InlineKeyboardBuilder()
    toggle_label = "🔴 Disable mandatory subscription" if force_sub_enabled else "🟢 Enable mandatory subscription"
    builder.row(InlineKeyboardButton(text=toggle_label, callback_data="settings_toggle_forcesub"))
    builder.row(InlineKeyboardButton(text="⬅️ Back", callback_data="admin_back"))
    return builder.as_markup()


@router.callback_query(F.data == "admin_settings")
async def settings_main(callback: CallbackQuery):
    force_sub = await get_setting("force_subscription", "1") == "1"
    admins_list = "\n".join(f"• <code>{admin_id}</code>" for admin_id in ADMIN_IDS) or "—"

    text = (
        "👑 <b>Admin Settings</b>\n\n"
        f"Mandatory subscription: {'🟢 Enabled' if force_sub else '🔴 Disabled'}\n\n"
        f"<b>Bot administrators:</b>\n{admins_list}\n\n"
        "ℹ️ To add or remove admins, update the ADMIN_IDS value in the .env file."
    )
    await callback.message.edit_text(text, reply_markup=_settings_keyboard(force_sub))
    await callback.answer()


@router.callback_query(F.data == "settings_toggle_forcesub")
async def toggle_force_sub(callback: CallbackQuery):
    current = await get_setting("force_subscription", "1") == "1"
    new_value = "0" if current else "1"
    await set_setting("force_subscription", new_value)

    force_sub = new_value == "1"
    admins_list = "\n".join(f"• <code>{admin_id}</code>" for admin_id in ADMIN_IDS) or "—"
    text = (
        "👑 <b>Admin Settings</b>\n\n"
        f"Mandatory subscription: {'🟢 Enabled' if force_sub else '🔴 Disabled'}\n\n"
        f"<b>Bot administrators:</b>\n{admins_list}\n\n"
        "ℹ️ To add or remove admins, update the ADMIN_IDS value in the .env file."
    )
    await callback.message.edit_text(text, reply_markup=_settings_keyboard(force_sub))
    await callback.answer("Updated.")
