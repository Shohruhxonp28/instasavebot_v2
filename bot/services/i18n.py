"""
Localization module for Uzbek, Russian, and English.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

SUPPORTED_LANGUAGES = {
    "uz": "🇺🇿 O'zbekcha",
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
}

DEFAULT_LANGUAGE = "uz"

TEXTS = {
    "choose_language_prompt": {
        "uz": (
            "🌐 <b>Iltimos, tilni tanlang:</b>\n"
            "🇷🇺 <b>Пожалуйста, выберите язык:</b>\n"
            "🇬🇧 <b>Please choose a language:</b>"
        ),
        "ru": (
            "🇷🇺 <b>Пожалуйста, выберите язык:</b>\n"
            "🇺🇿 <b>Iltimos, tilni tanlang:</b>\n"
            "🇬🇧 <b>Please choose a language:</b>"
        ),
        "en": (
            "🇬🇧 <b>Please choose a language:</b>\n"
            "🇺🇿 <b>Iltimos, tilni tanlang:</b>\n"
            "🇷🇺 <b>Пожалуйста, выберите язык:</b>"
        ),
    },
    "lang_selected_alert": {
        "uz": "✅ O'zbek tili tanlandi!",
        "ru": "✅ Выбран русский язык!",
        "en": "✅ English language selected!",
    },
    "welcome": {
        "uz": (
            "👋 <b>Universal Video Downloader Botiga xush kelibsiz!</b>\n\n"
            "Menga video yoki media havolasini yuboring va men uni sizga yuklab beraman. "
            "Shuningdek, videodagi musiqani aniqlab, MP3 formatda ajratib bera olaman!\n\n"
            "📌 <b>Qo'llab-quvvatlanadigan platformalar:</b>\n"
            "• Instagram (Reels, Post, Carousel, Stories)\n"
            "• Threads\n"
            "• TikTok & Douyin\n"
            "• Pinterest (Rasmlar va Videolar)\n"
            "• YouTube (Shorts va Videolar)\n"
            "• Facebook\n"
            "• Twitter (X)\n"
            "• Spotify & SoundCloud\n"
            "• Snapchat & CapCut\n"
            "• TeraBox, Reddit, Dailymotion, Tumblr, LinkedIn, Bluesky, Kuaishou\n\n"
            "💡 <i>Boshlash uchun havolani yuboring!</i>\n"
            "🌐 <i>Tilni o'zgartirish: /lang</i>"
        ),
        "ru": (
            "👋 <b>Добро пожаловать в Universal Video Downloader Bot!</b>\n\n"
            "Отправьте мне ссылку на видео или медиа, и я скачаю его для вас. "
            "Также я могу распознать музыку из видео и извлечь MP3 аудиодорожку!\n\n"
            "📌 <b>Поддерживаемые платформы:</b>\n"
            "• Instagram (Reels, посты, карусели, Stories)\n"
            "• Threads\n"
            "• TikTok & Douyin\n"
            "• Pinterest (фото и видео)\n"
            "• YouTube (Shorts и видео)\n"
            "• Facebook\n"
            "• Twitter (X)\n"
            "• Spotify & SoundCloud\n"
            "• Snapchat & CapCut\n"
            "• TeraBox, Reddit, Dailymotion, Tumblr, LinkedIn, Bluesky, Kuaishou\n\n"
            "💡 <i>Отправьте ссылку, чтобы начать!</i>\n"
            "🌐 <i>Сменить язык: /lang</i>"
        ),
        "en": (
            "👋 <b>Welcome to Universal Video Downloader Bot!</b>\n\n"
            "Send me a link to a video or media, and I'll download it for you. "
            "I can also identify the music playing in the video and extract the MP3 track!\n\n"
            "📌 <b>Supported platforms:</b>\n"
            "• Instagram (Reels, Posts, Carousel, Stories)\n"
            "• Threads\n"
            "• TikTok & Douyin\n"
            "• Pinterest (Images & Videos)\n"
            "• YouTube (Shorts & Videos)\n"
            "• Facebook\n"
            "• Twitter (X)\n"
            "• Spotify & SoundCloud\n"
            "• Snapchat & CapCut\n"
            "• TeraBox, Reddit, Dailymotion, Tumblr, LinkedIn, Bluesky, Kuaishou\n\n"
            "💡 <i>Just paste a link to get started!</i>\n"
            "🌐 <i>Change language: /lang</i>"
        ),
    },
    "subscribe_text": {
        "uz": (
            "🔒 Botdan foydalanish uchun quyidagi kanal(lar)ga a'zo bo'ling.\n\n"
            "A'zo bo'lgach, <b>✅ Obunani tekshirish</b> tugmasini bosing."
        ),
        "ru": (
            "🔒 Чтобы использовать бота, пожалуйста, подпишитесь на указанные каналы.\n\n"
            "После подписки нажмите кнопку <b>✅ Проверить подписку</b>."
        ),
        "en": (
            "🔒 To use this bot, please subscribe to the channel(s) below first.\n\n"
            "After subscribing, tap <b>✅ Check Subscription</b>."
        ),
    },
    "check_sub_btn": {
        "uz": "✅ Obunani tekshirish",
        "ru": "✅ Проверить подписку",
        "en": "✅ Check Subscription",
    },
    "sub_not_joined_alert": {
        "uz": "❌ Siz hali barcha majburiy kanallarga a'zo bo'lmadingiz.",
        "ru": "❌ Вы еще не подписались на все каналы.",
        "en": "❌ You still haven't joined all required channels.",
    },
    "sub_confirmed_alert": {
        "uz": "✅ Obuna tasdiqlandi!",
        "ru": "✅ Подписка подтверждена!",
        "en": "✅ Subscription confirmed!",
    },
    "downloading": {
        "uz": "⏳ Media yuklab olinmoqda, iltimos kuting...",
        "ru": "⏳ Скачиваем медиа, пожалуйста, подождите...",
        "en": "⏳ Downloading your media, please wait...",
    },
    "sending": {
        "uz": "📤 Media yuborilmoqda...",
        "ru": "📤 Отправка медиа...",
        "en": "📤 Sending your media...",
    },
    "download_error": {
        "uz": (
            "😔 Kechirasiz, ushbu mediani yuklab bo'lmadi.\n\n"
            "<b>Batafsil:</b> <code>{error}</code>\n\n"
            "Havola yopiq (profil private), qo'llab-quvvatlanmaydigan yoki vaqtincha ishlamayotgan bo'lishi mumkin."
        ),
        "ru": (
            "😔 К сожалению, не удалось скачать это медиа.\n\n"
            "<b>Подробности:</b> <code>{error}</code>\n\n"
            "Возможно, ссылка приватная, не поддерживается или временно недоступна."
        ),
        "en": (
            "😔 Sorry, I couldn't download this media.\n\n"
            "<b>Details:</b> <code>{error}</code>\n\n"
            "The link might be private, unsupported, or temporarily unavailable."
        ),
    },
    "unexpected_error": {
        "uz": (
            "😔 Mediani yuklashda kutilmagan xatolik yuz berdi.\n\n"
            "<b>Batafsil:</b> <code>{error}</code>"
        ),
        "ru": (
            "😔 Произошла ошибка при скачивании медиа.\n\n"
            "<b>Подробности:</b> <code>{error}</code>"
        ),
        "en": (
            "😔 An unexpected error occurred while downloading this media.\n\n"
            "<b>Details:</b> <code>{error}</code>"
        ),
    },
    "user_blocked": {
        "uz": "🚫 Siz ushbu botdan foydalanishdan bloklangansiz.",
        "ru": "🚫 Вы заблокированы в этом боте.",
        "en": "🚫 You have been blocked from using this bot.",
    },
    "send_error": {
        "uz": "😔 Media yuklab olindi, ammo yuborib bo'lmadi (fayl hajmi 50MB dan katta yoki format qo'llab-quvvatlanmaydi).",
        "ru": "😔 Медиа скачано, но не удалось отправить (файл больше 50 МБ или формат не поддерживается).",
        "en": "😔 The media was downloaded but could not be sent (file may exceed 50MB or format is unsupported).",
    },
    "download_audio_btn": {
        "uz": "📥 Qo'shiqni yuklab olish",
        "ru": "📥 Скачать аудио/музыку",
        "en": "📥 Download Music",
    },
    "audio_searching": {
        "uz": "🔍 <b>Videodagi musiqa qidirilmoqda...</b>",
        "ru": "🔍 <b>Поиск музыки из видео...</b>",
        "en": "🔍 <b>Searching for music in video...</b>",
    },
    "audio_found": {
        "uz": "🎶 Musiqa topildi: <b>{artist} - {title}</b>\n📥 Yuklanmoqda...",
        "ru": "🎶 Музыка найдена: <b>{artist} - {title}</b>\n📥 Загрузка...",
        "en": "🎶 Music found: <b>{artist} - {title}</b>\n📥 Downloading...",
    },
    "audio_caption_found": {
        "uz": "🎵 <b>{artist} - {title}</b>\n\n🎬 @{bot_username} orqali topildi va yuklandi",
        "ru": "🎵 <b>{artist} - {title}</b>\n\n🎬 Найдено и скачано с помощью @{bot_username}",
        "en": "🎵 <b>{artist} - {title}</b>\n\n🎬 Found and downloaded via @{bot_username}",
    },
    "audio_sending": {
        "uz": "📥 Qo'shiq yuborilmoqda...",
        "ru": "📥 Аудиодорожка отправляется...",
        "en": "📥 Sending audio track...",
    },
    "audio_expired": {
        "uz": "⚠️ Qo'shiq topilmadi yoki muddati o'tgan.",
        "ru": "⚠️ Аудио не найдено или срок действия истек.",
        "en": "⚠️ Audio track not found or expired.",
    },
    "audio_file_missing": {
        "uz": "⚠️ Qo'shiq fayli mavjud emas.",
        "ru": "⚠️ Файл аудио отсутствует.",
        "en": "⚠️ Audio file is missing.",
    },
    "audio_send_error": {
        "uz": "😔 Qo'shiqni yuborishda xatolik yuz berdi.",
        "ru": "😔 Ошибка при отправке аудио.",
        "en": "😔 Failed to send audio.",
    },
    "credit": {
        "uz": "🎬 @{bot_username} orqali yuklab olindi",
        "ru": "🎬 Скачано с помощью @{bot_username}",
        "en": "🎬 Downloaded via @{bot_username}",
    },
}


def t(key: str, lang: str | None = None, **kwargs) -> str:
    """
    Get localized string by key and language code.
    Falls back to 'uz' and then 'en' if key/language is missing.
    """
    selected_lang = lang if lang in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
    entry = TEXTS.get(key, {})
    template = entry.get(selected_lang) or entry.get(DEFAULT_LANGUAGE) or entry.get("en") or key
    if kwargs:
        try:
            return template.format(**kwargs)
        except Exception:
            return template
    return template


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Return inline keyboard with all 3 supported languages."""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="set_lang:uz"))
    builder.row(InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang:ru"))
    builder.row(InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang:en"))
    return builder.as_markup()
