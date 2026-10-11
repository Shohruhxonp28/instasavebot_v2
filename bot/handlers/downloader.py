import re

from aiogram import Router, F
from aiogram.types import Message, FSInputFile, InputMediaPhoto, InputMediaVideo

from bot.database.requests import is_user_blocked, log_download, log_recognition, touch_user
from bot.services.subscription import get_unsubscribed_channels
from bot.keyboards.subscription_kb import subscription_keyboard
from bot.services.downloader import (
    download_media,
    detect_platform,
    cleanup_media,
    cleanup_file,
    DownloadError,
    MediaItem,
)
from bot.services.audio import extract_audio, cleanup_file as cleanup_audio, AudioExtractionError
from bot.services.acrcloud import recognize_audio

router = Router()

URL_PATTERN = re.compile(r"https?://\S+")


@router.message(F.text.regexp(URL_PATTERN))
async def handle_video_link(message: Message):
    if await is_user_blocked(message.from_user.id):
        await message.answer("🚫 You have been blocked from using this bot.")
        return

    await touch_user(message.from_user.id)

    unsubscribed = await get_unsubscribed_channels(message.bot, message.from_user.id)
    if unsubscribed:
        await message.answer(
            "🔒 Please subscribe to the required channel(s) first.",
            reply_markup=subscription_keyboard(unsubscribed),
        )
        return

    match = URL_PATTERN.search(message.text)
    url = match.group(0)
    platform = detect_platform(url)

    status_message = await message.answer("⏳ Downloading your media, please wait...")

    items: list[MediaItem] = []
    audio_path = None
    try:
        items = download_media(url)
    except DownloadError:
        await log_download(message.from_user.id, platform, success=False)
        await status_message.edit_text(
            "😔 Sorry, I couldn't download this media. "
            "The link might be private, unsupported, or unavailable."
        )
        return
    except Exception:
        await log_download(message.from_user.id, platform, success=False)
        await status_message.edit_text(
            "😔 An error occurred while downloading this media. Please try again later."
        )
        return

    await log_download(message.from_user.id, platform, success=True)

    try:
        await status_message.edit_text("📤 Sending your media...")

        # Case 1: Single item
        if len(items) == 1:
            item = items[0]
            if item.media_type == "video":
                await message.answer_video(
                    FSInputFile(item.file_path),
                    caption=item.caption or "✅ Here is your video!",
                )
            elif item.media_type == "audio":
                await message.answer_audio(
                    FSInputFile(item.file_path),
                    caption=item.caption or "✅ Here is your audio!",
                )
            else:
                await message.answer_photo(
                    FSInputFile(item.file_path),
                    caption=item.caption or "✅ Here is your photo!",
                )

        # Case 2: Multiple items (Carousel / Album)
        else:
            for i in range(0, len(items), 10):
                chunk = items[i : i + 10]
                media_group = []
                for idx, it in enumerate(chunk):
                    file_input = FSInputFile(it.file_path)
                    caption = "✅ Here is your media!" if (i == 0 and idx == 0) else None
                    if it.media_type == "video":
                        media_group.append(InputMediaVideo(media=file_input, caption=caption))
                    else:
                        media_group.append(InputMediaPhoto(media=file_input, caption=caption))
                await message.answer_media_group(media=media_group)

    except Exception:
        await status_message.edit_text(
            "😔 The media was downloaded but could not be sent (file may be too large or format unsupported)."
        )
        cleanup_media(items)
        return

    # Music recognition (only if there is at least one video)
    first_video = next((it for it in items if it.media_type == "video"), None)
    if first_video:
        try:
            await status_message.edit_text("🎧 Trying to identify the music...")
            audio_path = extract_audio(first_video.file_path)
            result = recognize_audio(audio_path)
        except AudioExtractionError:
            result = None
        except Exception:
            result = None

        if result:
            await log_recognition(message.from_user.id, success=True)
            text = (
                f"🎵 <b>Song:</b> {result.title}\n"
                f"👤 <b>Artist:</b> {result.artist or 'Unknown'}\n"
            )
            if result.album:
                text += f"💿 <b>Album:</b> {result.album}\n"
            text += f"🎯 <b>Confidence:</b> {result.score}%"
            await status_message.edit_text(text)
        else:
            await log_recognition(message.from_user.id, success=False)
            try:
                await status_message.delete()
            except Exception:
                await status_message.edit_text("🎵 Music could not be identified.")
    else:
        # For photos, remove the downloading status message
        try:
            await status_message.delete()
        except Exception:
            pass

    # Clean up temporary media and audio files
    cleanup_media(items)
    if audio_path:
        cleanup_audio(audio_path)
