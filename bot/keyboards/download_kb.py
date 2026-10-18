from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


from bot.services.i18n import t


def audio_download_keyboard(audio_token: str, lang: str = "uz") -> InlineKeyboardMarkup:
    """
    Inline keyboard with a button to download the song/audio track.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("download_audio_btn", lang),
                    callback_data=f"get_audio:{audio_token}",
                )
            ]
        ]
    )
