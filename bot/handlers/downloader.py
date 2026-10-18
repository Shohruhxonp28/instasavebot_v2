import os
import uuid
import logging
import re

logger = logging.getLogger(__name__)

from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    FSInputFile,
    InputMediaPhoto,
    InputMediaVideo,
)

from bot.database.requests import (
    is_user_blocked,
    log_download,
    log_recognition,
    touch_user,
    get_user_language,
)
from bot.services.subscription import get_unsubscribed_channels
from bot.keyboards.subscription_kb import subscription_keyboard
from bot.keyboards.download_kb import audio_download_keyboard
from bot.services.downloader import (
    download_media,
    detect_platform,
    cleanup_media,
    cleanup_file,
    DownloadError,
    MediaItem,
)
from bot.services.audio import (
    extract_audio,
    extract_full_audio,
    cleanup_file as cleanup_audio,
)
from bot.services.acrcloud import recognize_audio
from bot.services.audio_cache import audio_cache
from bot.services.i18n import t

router = Router()

URL_PATTERN = re.compile(r"https?://\S+")
_bot_username: str | None = None


async def _get_bot_username(bot) -> str:
    global _bot_username
    if not _bot_username:
        try:
            me = await bot.get_me()
            _bot_username = me.username or "instasavebot"
        except Exception:
            _bot_username = "instasavebot"
    return _bot_username


def _format_caption(original_caption: str | None, bot_username: str, lang: str = "uz") -> str:
    credit = t("credit", lang, bot_username=bot_username)
    if original_caption and original_caption.strip():
        text = original_caption.strip()
        max_len = 1024 - len(credit) - 4
        if len(text) > max_len:
            text = text[:max_len] + "..."
        return f"{text}\n\n{credit}"
    return credit


@router.message(F.text.regexp(URL_PATTERN))
async def handle_video_link(message: Message):
    lang = await get_user_language(message.from_user.id) or "uz"

    if await is_user_blocked(message.from_user.id):
        await message.answer(t("user_blocked", lang))
        return

    await touch_user(message.from_user.id)

    unsubscribed = await get_unsubscribed_channels(message.bot, message.from_user.id)
    if unsubscribed:
        await message.answer(
            t("subscribe_text", lang),
            reply_markup=subscription_keyboard(unsubscribed, lang=lang),
        )
        return

    match = URL_PATTERN.search(message.text)
    url = match.group(0)
    platform = detect_platform(url)

    status_message = await message.answer(t("downloading", lang))

    items: list[MediaItem] = []
    try:
        items = download_media(url)
    except DownloadError as e:
        logger.error("DownloadError for url %s: %s", url, e)
        await log_download(message.from_user.id, platform, success=False)
        await status_message.edit_text(
            t("download_error", lang, error=str(e)[:200])
        )
        return
    except Exception as e:
        logger.exception("Unexpected error downloading %s: %s", url, e)
        await log_download(message.from_user.id, platform, success=False)
        await status_message.edit_text(
            t("unexpected_error", lang, error=str(e)[:200])
        )
        return

    await log_download(message.from_user.id, platform, success=True)
    bot_username = await _get_bot_username(message.bot)

    # Prepare audio extraction & music recognition if there is a video
    first_video = next((it for it in items if it.media_type == "video"), None)
    audio_token = None

    if first_video:
        sample_path = None
        song_title = None
        song_artist = None

        # 1. Recognize music with ACRCloud
        try:
            sample_path = extract_audio(first_video.file_path, duration_seconds=20)
            rec_result = recognize_audio(sample_path)
            if rec_result:
                song_title = rec_result.title
                song_artist = rec_result.artist
                await log_recognition(message.from_user.id, success=True)
            else:
                await log_recognition(message.from_user.id, success=False)
        except Exception as e:
            logger.debug("Music recognition error: %s", e)
        finally:
            if sample_path:
                cleanup_audio(sample_path)

        if not song_title:
            if first_video.caption and first_video.caption.strip():
                song_title = first_video.caption.strip().split("\n")[0][:60]
            else:
                song_title = "Audio track"
            song_artist = f"@{bot_username}"

        # 2. Extract full MP3 audio track
        try:
            full_audio_path = extract_full_audio(
                first_video.file_path,
                title=song_title,
                artist=song_artist,
            )
            audio_token = uuid.uuid4().hex[:12]
            audio_cache.store(
                token=audio_token,
                audio_path=full_audio_path,
                title=song_title,
                artist=song_artist,
                bot_username=bot_username,
            )
        except Exception as e:
            logger.warning("Could not extract full audio: %s", e)
            audio_token = None

    keyboard = audio_download_keyboard(audio_token, lang=lang) if audio_token else None

    try:
        await status_message.edit_text(t("sending", lang))

        # Case 1: Single item
        if len(items) == 1:
            item = items[0]
            caption = _format_caption(item.caption, bot_username, lang=lang)
            if item.media_type == "video":
                await message.answer_video(
                    FSInputFile(item.file_path),
                    caption=caption,
                    reply_markup=keyboard,
                )
            elif item.media_type == "audio":
                await message.answer_audio(
                    FSInputFile(item.file_path),
                    caption=caption,
                )
            else:
                await message.answer_photo(
                    FSInputFile(item.file_path),
                    caption=caption,
                )

        # Case 2: Multiple items (Carousel / Album)
        else:
            for i in range(0, len(items), 10):
                chunk = items[i : i + 10]
                media_group = []
                for idx, it in enumerate(chunk):
                    file_input = FSInputFile(it.file_path)
                    caption = _format_caption(it.caption, bot_username, lang=lang) if (i == 0 and idx == 0) else None
                    if it.media_type == "video":
                        media_group.append(InputMediaVideo(media=file_input, caption=caption))
                    else:
                        media_group.append(InputMediaPhoto(media=file_input, caption=caption))
                await message.answer_media_group(media=media_group)

            if keyboard:
                await message.answer(
                    t("credit", lang, bot_username=bot_username),
                    reply_markup=keyboard,
                )

        # Clean status message after sending media
        try:
            await status_message.delete()
        except Exception:
            pass

    except Exception as e:
        logger.exception("Failed to send media: %s", e)
        await status_message.edit_text(t("send_error", lang))
    finally:
        # Clean up temporary downloaded video / images
        cleanup_media(items)


@router.callback_query(F.data.startswith("get_audio:"))
async def handle_get_audio(callback: CallbackQuery):
    lang = await get_user_language(callback.from_user.id) or "uz"
    token = callback.data.split(":", 1)[1]
    item = audio_cache.get(token)

    if not item:
        await callback.answer(t("audio_expired", lang), show_alert=True)
        return

    await callback.answer(t("audio_sending", lang))

    bot_username = item.bot_username or "bot"
    audio_caption = t("credit", lang, bot_username=bot_username)

    try:
        if item.file_id:
            await callback.message.reply_audio(
                audio=item.file_id,
                caption=audio_caption,
                title=item.title,
                performer=item.artist,
            )
        elif item.audio_path and os.path.exists(item.audio_path):
            sent = await callback.message.reply_audio(
                audio=FSInputFile(item.audio_path),
                caption=audio_caption,
                title=item.title,
                performer=item.artist,
            )
            if sent.audio:
                item.file_id = sent.audio.file_id
                # Remove file from local disk to save space now that Telegram cloud cached it
                cleanup_file(item.audio_path)
                item.audio_path = None
        else:
            await callback.answer(t("audio_file_missing", lang), show_alert=True)
    except Exception as e:
        logger.exception("Failed to send audio for token %s: %s", token, e)
        await callback.answer(t("audio_send_error", lang), show_alert=True)
