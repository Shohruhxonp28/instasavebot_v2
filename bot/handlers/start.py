from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from bot.database.requests import add_user, is_user_blocked
from bot.services.subscription import get_unsubscribed_channels
from bot.keyboards.subscription_kb import subscription_keyboard
from bot.config import SUPPORTED_PLATFORMS

router = Router()

WELCOME_TEXT = (
    "👋 <b>Welcome to Video Downloader Bot!</b>\n\n"
    "Send me a link to a video and I'll download it for you. "
    "I can also try to recognize the music playing in the video.\n\n"
    "📌 <b>Supported platforms:</b>\n"
    + "\n".join(f"• {p}" for p in SUPPORTED_PLATFORMS)
    + "\n\nJust paste a link to get started!"
)

SUBSCRIBE_TEXT = (
    "🔒 To use this bot, please subscribe to the channel(s) below first.\n\n"
    "After subscribing, tap <b>✅ Check Subscription</b>."
)


@router.message(CommandStart())
async def cmd_start(message: Message):
    if await is_user_blocked(message.from_user.id):
        await message.answer("🚫 You have been blocked from using this bot.")
        return

    await add_user(message.from_user.id, message.from_user.username, message.from_user.first_name)

    unsubscribed = await get_unsubscribed_channels(message.bot, message.from_user.id)
    if unsubscribed:
        await message.answer(SUBSCRIBE_TEXT, reply_markup=subscription_keyboard(unsubscribed))
        return

    await message.answer(WELCOME_TEXT)


@router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: CallbackQuery):
    unsubscribed = await get_unsubscribed_channels(callback.bot, callback.from_user.id)
    if unsubscribed:
        await callback.answer("❌ You still haven't joined all channels.", show_alert=True)
        return

    await callback.message.edit_text(WELCOME_TEXT)
    await callback.answer("✅ Subscription confirmed!")
