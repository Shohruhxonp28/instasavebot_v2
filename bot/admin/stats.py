from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.utils.filters import IsAdmin
from bot.database.requests import get_stats
from bot.keyboards.admin_kb import back_to_admin_menu

router = Router()
router.callback_query.filter(IsAdmin())


@router.callback_query(F.data == "admin_stats")
async def show_stats(callback: CallbackQuery):
    stats = await get_stats()

    text = (
        "📊 <b>Statistics</b>\n\n"
        f"👥 Total users: <b>{stats['total_users']}</b>\n"
        f"🟢 Active today: <b>{stats['active_today']}</b>\n\n"
        f"📥 Total downloads: <b>{stats['total_downloads']}</b>\n"
        f"  • TikTok: <b>{stats['tiktok']}</b>\n"
        f"  • Instagram: <b>{stats['instagram']}</b>\n"
        f"  • YouTube: <b>{stats['youtube']}</b>\n\n"
        f"🎵 Songs recognized: <b>{stats['recognized']}</b>\n"
        f"❌ Failed recognitions: <b>{stats['failed_recognitions']}</b>"
    )

    await callback.message.edit_text(text, reply_markup=back_to_admin_menu())
    await callback.answer()
