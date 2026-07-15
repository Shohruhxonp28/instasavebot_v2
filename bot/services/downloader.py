"""
Video downloading using yt-dlp.
"""
import os
import uuid
import yt_dlp
from bot.config import DOWNLOADS_DIR, MAX_VIDEO_SIZE_MB, FFMPEG_PATH


class DownloadError(Exception):
    """Raised when a video could not be downloaded."""


def detect_platform(url: str) -> str:
    """Roughly detect the platform name from the URL, used for stats/logging."""
    url = url.lower()
    if "tiktok.com" in url:
        return "TikTok"
    if "instagram.com" in url:
        return "Instagram"
    if "youtube.com" in url or "youtu.be" in url:
        return "YouTube"
    if "facebook.com" in url or "fb.watch" in url:
        return "Facebook"
    if "twitter.com" in url or "x.com" in url:
        return "Twitter (X)"
    return "Unknown"


def download_video(url: str) -> str:
    """
    Download a video using yt-dlp and return the local file path.
    Raises DownloadError on failure.
    """
    file_id = str(uuid.uuid4())
    output_template = os.path.join(DOWNLOADS_DIR, f"{file_id}.%(ext)s")

    ydl_opts = {
        "outtmpl": output_template,
        # Try progressive (single-file, no merge needed) mp4 first, then fall
        # back to best video+audio (requires ffmpeg to merge), then anything.
        "format": "best[ext=mp4]/bv*+ba/best",
        "merge_output_format": "mp4",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "max_filesize": MAX_VIDEO_SIZE_MB * 1024 * 1024,
    }

    if FFMPEG_PATH:
        ydl_opts["ffmpeg_location"] = FFMPEG_PATH

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            if not os.path.exists(file_path):
                # Extension may differ after merging/post-processing
                base, _ = os.path.splitext(file_path)
                for ext in (".mp4", ".mkv", ".webm"):
                    candidate = base + ext
                    if os.path.exists(candidate):
                        file_path = candidate
                        break
            if not os.path.exists(file_path):
                raise DownloadError("File was not created after download.")
            return file_path
    except yt_dlp.utils.DownloadError as e:
        raise DownloadError(str(e)) from e
    except Exception as e:
        raise DownloadError(str(e)) from e


def cleanup_file(file_path: str) -> None:
    """Remove a downloaded file if it exists."""
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except OSError:
        pass
