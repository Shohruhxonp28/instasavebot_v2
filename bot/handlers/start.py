from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from bot.database.requests import (
    add_user,
    is_user_blocked,
    get_user_language,
    set_user_language,
)
from bot.services.subscription import get_unsubscribed_channels
from bot.keyboards.subscription_kb import subscription_keyboard
from bot.services.i18n import t, get_language_keyboard, SUPPORTED_LANGUAGES

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """
    On /start, register user and immediately prompt to choose language first of all.
    """
    if await is_user_blocked(message.from_user.id):
        lang = await get_user_language(message.from_user.id) or "uz"
        await message.answer(t("user_blocked", lang))
        return

    await add_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
    )

    # Prompt language selection first
    await message.answer(
        t("choose_language_prompt"),
        reply_markup=get_language_keyboard(),
    )


@router.message(Command(commands=["lang", "language"]))
async def cmd_language(message: Message):
    """Allow user to change language at any time."""
    if await is_user_blocked(message.from_user.id):
        return
    await message.answer(
        t("choose_language_prompt"),
        reply_markup=get_language_keyboard(),
    )


@router.callback_query(F.data.startswith("set_lang:"))
async def set_language_callback(callback: CallbackQuery):
    """Handle language selection."""
    lang_code = callback.data.split(":", 1)[1]
    if lang_code not in SUPPORTED_LANGUAGES:
        lang_code = "uz"

    await set_user_language(callback.from_user.id, lang_code)
    await callback.answer(t("lang_selected_alert", lang_code))

    # Check required channels after language is selected
    unsubscribed = await get_unsubscribed_channels(callback.bot, callback.from_user.id)
    if unsubscribed:
        await callback.message.edit_text(
            t("subscribe_text", lang_code),
            reply_markup=subscription_keyboard(unsubscribed, lang=lang_code),
        )
        return

    # Show welcome message in selected language
    await callback.message.edit_text(t("welcome", lang_code))


@router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: CallbackQuery):
    """Check required channel subscriptions."""
    lang = await get_user_language(callback.from_user.id) or "uz"

    unsubscribed = await get_unsubscribed_channels(callback.bot, callback.from_user.id)
    if unsubscribed:
        await callback.answer(t("sub_not_joined_alert", lang), show_alert=True)
        return

    await callback.message.edit_text(t("welcome", lang))
    await callback.answer(t("sub_confirmed_alert", lang))
