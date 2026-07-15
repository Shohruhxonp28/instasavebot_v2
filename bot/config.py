"""
Configuration loader.
Reads all settings from environment variables (.env file).
"""
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")

# Admin Telegram IDs, e.g. "111111111,222222222"
ADMIN_IDS: list[int] = [
    int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()
]

# ACRCloud credentials
ACR_HOST: str = os.getenv("ACR_HOST", "")
ACR_ACCESS_KEY: str = os.getenv("ACR_ACCESS_KEY", "")
ACR_ACCESS_SECRET: str = os.getenv("ACR_ACCESS_SECRET", "")

# Database
DB_PATH: str = os.getenv("DB_PATH", "bot_database.db")

# Folders
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOWNLOADS_DIR = os.path.join(BASE_DIR, "downloads")
MEDIA_DIR = os.path.join(BASE_DIR, "media")

os.makedirs(DOWNLOADS_DIR, exist_ok=True)
os.makedirs(MEDIA_DIR, exist_ok=True)

# Telegram upload limit (Bot API allows up to 50MB for direct upload)
MAX_VIDEO_SIZE_MB: int = int(os.getenv("MAX_VIDEO_SIZE_MB", "50"))

# Optional: full path to ffmpeg.exe / ffmpeg binary, only needed if ffmpeg
# is NOT already on your system PATH (common on Windows).
# Example: C:\ffmpeg\bin\ffmpeg.exe
FFMPEG_PATH: str = os.getenv("FFMPEG_PATH", "")

SUPPORTED_PLATFORMS = ["TikTok", "Instagram Reels", "YouTube", "Facebook", "Twitter (X)"]
