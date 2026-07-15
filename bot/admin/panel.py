from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.utils.filters import IsAdmin
from bot.keyboards.admin_kb import admin_main_menu

router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

ADMIN_MENU_TEXT = "👑 <b>Admin Panel</b>\n\nChoose an option below:"


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(ADMIN_MENU_TEXT, reply_markup=admin_main_menu())


@router.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(ADMIN_MENU_TEXT, reply_markup=admin_main_menu())
    await callback.answer()


@router.callback_query(F.data == "admin_exit")
async def admin_exit(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Admin panel closed.")
    await callback.answer()
