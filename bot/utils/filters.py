from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from bot.config import ADMIN_IDS


class IsAdmin(BaseFilter):
    """Allows the handler to run only for configured admin Telegram IDs."""

    async def __call__(self, event: Message | CallbackQuery) -> bool:
        return event.from_user.id in ADMIN_IDS
