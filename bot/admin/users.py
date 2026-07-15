from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.utils.filters import IsAdmin
from bot.utils.states import UserSearchStates
from bot.database.requests import get_user, count_total_users, set_user_blocked
from bot.keyboards.admin_kb import users_menu, user_actions_menu, back_to_admin_menu

router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


@router.callback_query(F.data == "admin_users")
async def users_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    total = await count_total_users()
    text = f"👥 <b>Users</b>\n\nTotal registered users: <b>{total}</b>"
    await callback.message.edit_text(text, reply_markup=users_menu())
    await callback.answer()


@router.callback_query(F.data == "users_search")
async def users_search_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🔎 Send the Telegram ID of the user you want to find.",
        reply_markup=back_to_admin_menu(),
    )
    await state.set_state(UserSearchStates.waiting_id)
    await callback.answer()


@router.message(UserSearchStates.waiting_id)
async def users_search_result(message: Message, state: FSMContext):
    await state.clear()

    if not message.text or not message.text.strip().isdigit():
        await message.answer("⚠️ Please send a valid numeric Telegram ID.", reply_markup=back_to_admin_menu())
        return

    telegram_id = int(message.text.strip())
    user = await get_user(telegram_id)

    if not user:
        await message.answer("❌ No user found with that ID.", reply_markup=back_to_admin_menu())
        return

    status = "🚫 Blocked" if user["is_blocked"] else "✅ Active"
    text = (
        f"👤 <b>User Info</b>\n\n"
        f"ID: <code>{user['telegram_id']}</code>\n"
        f"Username: @{user['username'] or '—'}\n"
        f"Name: {user['first_name'] or '—'}\n"
        f"Status: {status}\n"
        f"Joined: {user['created_at']}\n"
        f"Last active: {user['last_active']}"
    )

    await message.answer(text, reply_markup=user_actions_menu(telegram_id, bool(user["is_blocked"])))


@router.callback_query(F.data.startswith("block_"))
async def block_user(callback: CallbackQuery):
    telegram_id = int(callback.data.split("_", 1)[1])
    await set_user_blocked(telegram_id, True)
    await callback.answer("🚫 User blocked.")
    user = await get_user(telegram_id)
    await callback.message.edit_reply_markup(reply_markup=user_actions_menu(telegram_id, bool(user["is_blocked"])))


@router.callback_query(F.data.startswith("unblock_"))
async def unblock_user(callback: CallbackQuery):
    telegram_id = int(callback.data.split("_", 1)[1])
    await set_user_blocked(telegram_id, False)
    await callback.answer("✅ User unblocked.")
    user = await get_user(telegram_id)
    await callback.message.edit_reply_markup(reply_markup=user_actions_menu(telegram_id, bool(user["is_blocked"])))
