import asyncio

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from bot.utils.filters import IsAdmin
from bot.utils.states import BroadcastStates
from bot.database.requests import get_all_user_ids
from bot.keyboards.admin_kb import broadcast_confirm_menu, admin_main_menu

router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

@router.callback_query(F.data == "admin_broadcast")
async def broadcast_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "📢 <b>Broadcast Message</b>\n\nFoydalanuvchilarga yubormoqchi bo'lgan postni yuboring (Text, Photo, Video, va hkz):"
    )
    await state.set_state(BroadcastStates.waiting_content)
    await callback.answer()


@router.message(BroadcastStates.waiting_content)
async def broadcast_receive_content(message: Message, state: FSMContext):
    if message.text and message.text.startswith("/"):
        await message.answer("⚠️ Iltimos, komanda emas, oddiy xabar yuboring.")
        return

    await state.update_data(source_chat_id=message.chat.id, source_message_id=message.message_id)
    await state.set_state(BroadcastStates.confirming)

    # Show a preview by copying the message back to the admin
    await message.bot.copy_message(
        chat_id=message.chat.id,
        from_chat_id=message.chat.id,
        message_id=message.message_id,
    )
    await message.answer(
        "⬆️ This is a preview of your message.\n\nSend this message to all users?",
        reply_markup=broadcast_confirm_menu(),
    )


@router.callback_query(BroadcastStates.confirming, F.data == "broadcast_cancel")
async def broadcast_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Broadcast cancelled.", reply_markup=admin_main_menu())
    await callback.answer()


@router.callback_query(BroadcastStates.confirming, F.data == "broadcast_send")
async def broadcast_send(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    source_chat_id = data.get("source_chat_id")
    source_message_id = data.get("source_message_id")
    await state.clear()

    await callback.message.edit_text("📤 Sending broadcast, please wait...")
    await callback.answer()

    user_ids = await get_all_user_ids()
    success, failed = 0, 0

    for user_id in user_ids:
        try:
            await callback.bot.copy_message(
                chat_id=user_id,
                from_chat_id=source_chat_id,
                message_id=source_message_id,
            )
            success += 1
        except (TelegramForbiddenError, TelegramBadRequest):
            failed += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)  # gentle rate limiting

    await callback.message.answer(
        "✅ <b>Broadcast completed.</b>\n\n"
        f"Successful: {success}\n"
        f"Failed: {failed}",
        reply_markup=admin_main_menu(),
    )
