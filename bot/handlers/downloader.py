import re

from aiogram import Router, F
from aiogram.types import Message, FSInputFile

from bot.database.requests import is_user_blocked, log_download, log_recognition, touch_user
from bot.services.subscription import get_unsubscribed_channels
from bot.keyboards.subscription_kb import subscription_keyboard
from bot.services.downloader import download_video, detect_platform, cleanup_file, DownloadError
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

    status_message = await message.answer("⏳ Downloading your video, please wait...")

    video_path = None
    audio_path = None
    try:
        video_path = download_video(url)
    except DownloadError:
        await log_download(message.from_user.id, platform, success=False)
        await status_message.edit_text(
            "😔 Sorry, I couldn't download this video. "
            "The link might be private, unsupported, or unavailable."
        )
        return

    await log_download(message.from_user.id, platform, success=True)

    try:
        await status_message.edit_text("📤 Sending your video...")
        await message.answer_video(FSInputFile(video_path), caption="✅ Here is your video!")
    except Exception:
        await status_message.edit_text("😔 The video was downloaded but could not be sent (file may be too large).")
        cleanup_file(video_path)
        return

    # Music recognition
    await status_message.edit_text("🎧 Trying to identify the music...")
    try:
        audio_path = extract_audio(video_path)
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
        await status_message.edit_text("🎵 Music could not be identified.")

    cleanup_file(video_path)
    if audio_path:
        cleanup_audio(audio_path)
