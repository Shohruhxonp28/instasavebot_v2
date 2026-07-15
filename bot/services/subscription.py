"""
Checks whether a user is subscribed to all active required channels.
"""
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

from bot.database.requests import get_active_required_channels, get_setting

NOT_MEMBER_STATUSES = {"left", "kicked"}


async def get_unsubscribed_channels(bot: Bot, user_id: int) -> list:
    """Return the list of active required channels the user is NOT a member of."""
    force_sub = await get_setting("force_subscription", "1") == "1"
    if not force_sub:
        return []

    channels = await get_active_required_channels()
    unsubscribed = []

    for channel in channels:
        try:
            member = await bot.get_chat_member(chat_id=channel["channel_id"], user_id=user_id)
            if member.status in NOT_MEMBER_STATUSES:
                unsubscribed.append(channel)
        except TelegramBadRequest:
            # Bot may not be an admin in the channel, or channel_id is invalid.
            # We skip enforcing that particular channel rather than blocking everyone.
            continue

    return unsubscribed


async def is_user_subscribed(bot: Bot, user_id: int) -> bool:
    unsubscribed = await get_unsubscribed_channels(bot, user_id)
    return len(unsubscribed) == 0
