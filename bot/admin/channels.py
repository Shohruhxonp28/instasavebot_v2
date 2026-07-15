from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.utils.filters import IsAdmin
from bot.utils.states import ChannelStates
from bot.database.requests import (
    get_all_required_channels,
    get_required_channel,
    add_required_channel,
    remove_required_channel,
    toggle_required_channel,
)
from bot.keyboards.admin_kb import channels_menu, channel_detail_menu, back_to_admin_menu

router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


@router.callback_query(F.data == "admin_channels")
async def channels_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    channels = await get_all_required_channels()
    text = "📺 <b>Required Channels</b>\n\nTap a channel to manage it, or add a new one."
    await callback.message.edit_text(text, reply_markup=channels_menu(channels))
    await callback.answer()


@router.callback_query(F.data == "channel_add")
async def channel_add_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "➕ Send the channel username (e.g. <code>@mychannel</code>) or numeric channel ID.\n\n"
        "⚠️ The bot must be an <b>admin</b> in that channel to check subscriptions.",
        reply_markup=back_to_admin_menu(),
    )
    await state.set_state(ChannelStates.waiting_channel)
    await callback.answer()


@router.message(ChannelStates.waiting_channel)
async def channel_add_finish(message: Message, state: FSMContext):
    await state.clear()
    raw = message.text.strip()

    try:
        chat = await message.bot.get_chat(raw)
    except Exception:
        await message.answer(
            "❌ Couldn't find that channel. Make sure the username/ID is correct "
            "and the bot has been added as an admin there.",
            reply_markup=back_to_admin_menu(),
        )
        return

    username = f"@{chat.username}" if chat.username else None
    await add_required_channel(str(chat.id), username, chat.title)

    channels = await get_all_required_channels()
    await message.answer(
        f"✅ Added: <b>{chat.title}</b>",
        reply_markup=channels_menu(channels),
    )


@router.callback_query(F.data.startswith("chinfo_"))
async def channel_info(callback: CallbackQuery):
    channel_db_id = int(callback.data.split("_", 1)[1])
    channel = await get_required_channel(channel_db_id)
    if not channel:
        await callback.answer("Channel not found.", show_alert=True)
        return

    status = "🟢 Active" if channel["active"] else "🔴 Disabled"
    text = (
        f"📺 <b>{channel['title'] or channel['username'] or channel['channel_id']}</b>\n\n"
        f"ID: <code>{channel['channel_id']}</code>\n"
        f"Username: {channel['username'] or '—'}\n"
        f"Status: {status}"
    )
    await callback.message.edit_text(
        text, reply_markup=channel_detail_menu(channel_db_id, bool(channel["active"]))
    )
    await callback.answer()


@router.callback_query(F.data.startswith("chtoggle_"))
async def channel_toggle(callback: CallbackQuery):
    channel_db_id = int(callback.data.split("_", 1)[1])
    await toggle_required_channel(channel_db_id)
    channel = await get_required_channel(channel_db_id)
    await callback.answer("Status updated.")
    status = "🟢 Active" if channel["active"] else "🔴 Disabled"
    text = (
        f"📺 <b>{channel['title'] or channel['username'] or channel['channel_id']}</b>\n\n"
        f"ID: <code>{channel['channel_id']}</code>\n"
        f"Username: {channel['username'] or '—'}\n"
        f"Status: {status}"
    )
    await callback.message.edit_text(
        text, reply_markup=channel_detail_menu(channel_db_id, bool(channel["active"]))
    )


@router.callback_query(F.data.startswith("chremove_"))
async def channel_remove(callback: CallbackQuery):
    channel_db_id = int(callback.data.split("_", 1)[1])
    await remove_required_channel(channel_db_id)
    channels = await get_all_required_channels()
    await callback.answer("🗑 Channel removed.")
    await callback.message.edit_text(
        "📺 <b>Required Channels</b>\n\nTap a channel to manage it, or add a new one.",
        reply_markup=channels_menu(channels),
    )
