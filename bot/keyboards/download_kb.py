from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def audio_download_keyboard(audio_token: str) -> InlineKeyboardMarkup:
    """
    Inline keyboard with a button to download the song/audio track.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📥 Qo'shiqni yuklab olish",
                    callback_data=f"get_audio:{audio_token}",
                )
            ]
        ]
    )
