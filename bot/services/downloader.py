"""
Media downloading service supporting Instagram (Reels, Posts, Carousel),
Pinterest (Images, Videos), TikTok, YouTube, Facebook, Twitter (X) and more.
"""
import os
import re
import uuid
from dataclasses import dataclass
from typing import Literal

import requests
import yt_dlp
from yt_dlp.extractor.instagram import InstagramIE

try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except Exception:
    pass

from bot.config import (
    DOWNLOADS_DIR,
    MAX_VIDEO_SIZE_MB,
    FFMPEG_PATH,
    INSTAGRAM_USERNAME,
    INSTAGRAM_PASSWORD,
)


# Monkey-patch InstagramIE to prevent raising ExtractorError on photo-only posts
_orig_raise_no_formats = InstagramIE.raise_no_formats

def _patched_raise_no_formats(self, msg, *args, **kwargs):
    if "There is no video in this post" in str(msg):
        return
    return _orig_raise_no_formats(self, msg, *args, **kwargs)

InstagramIE.raise_no_formats = _patched_raise_no_formats


from bot.services.universal import (
    call_universal_downloader,
    parse_and_download_universal,
)


@dataclass
class MediaItem:
    media_type: Literal["video", "photo", "audio"]
    file_path: str
    caption: str = ""


class DownloadError(Exception):
    """Raised when media could not be downloaded."""


def detect_platform(url: str) -> str:
    """Roughly detect the platform name from the URL, used for stats/logging."""
    url = url.lower()
    if "tiktok.com" in url:
        return "TikTok"
    if "douyin.com" in url:
        return "Douyin"
    if "kuaishou.com" in url:
        return "Kuaishou"
    if "instagram.com" in url:
        return "Instagram"
    if "pinterest.com" in url or "pin.it" in url:
        return "Pinterest"
    if "threads.net" in url:
        return "Threads"
    if "spotify.com" in url or "open.spotify" in url:
        return "Spotify"
    if "snapchat.com" in url:
        return "Snapchat"
    if "capcut.com" in url:
        return "CapCut"
    if any(x in url for x in ("terabox", "1024tera", "terafileshare")):
        return "TeraBox"
    if "soundcloud.com" in url:
        return "SoundCloud"
    if "bsky.app" in url:
        return "Bluesky"
    if "reddit.com" in url:
        return "Reddit"
    if "dailymotion.com" in url:
        return "Dailymotion"
    if "tumblr.com" in url:
        return "Tumblr"
    if "linkedin.com" in url:
        return "LinkedIn"
    if "youtube.com" in url or "youtu.be" in url:
        return "YouTube"
    if "facebook.com" in url or "fb.watch" in url:
        return "Facebook"
    if "twitter.com" in url or "x.com" in url:
        return "Twitter (X)"
    return "Unknown"


def normalize_url(url: str) -> str:
    """Resolve shortened URLs like pin.it."""
    clean_url = url.strip()
    if "pin.it" in clean_url.lower():
        try:
            resp = requests.head(clean_url, allow_redirects=True, timeout=10)
            if resp.url:
                return resp.url
        except Exception:
            try:
                resp = requests.get(clean_url, allow_redirects=True, timeout=10)
                if resp.url:
                    return resp.url
            except Exception:
                pass
    return clean_url


def _get_cookies_path() -> str | None:
    cookies_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "cookies.txt",
    )
    return cookies_path if os.path.exists(cookies_path) else None


def download_file_from_url(url: str, ext: str = "jpg") -> str:
    """Download a raw file from a direct HTTP URL and save to downloads folder."""
    file_id = str(uuid.uuid4())
    file_path = os.path.join(DOWNLOADS_DIR, f"{file_id}.{ext}")
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers, stream=True, timeout=30)
    resp.raise_for_status()

    max_bytes = MAX_VIDEO_SIZE_MB * 1024 * 1024
    total_bytes = 0
    with open(file_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                total_bytes += len(chunk)
                if total_bytes > max_bytes:
                    raise DownloadError(f"File exceeds maximum size of {MAX_VIDEO_SIZE_MB}MB.")
                f.write(chunk)

    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        cleanup_file(file_path)
        raise DownloadError("Downloaded file is empty.")

    return file_path


def _download_pinterest(url: str) -> list[MediaItem]:
    """Download Pinterest media (image or video)."""
    resolved_url = normalize_url(url)

    # 1. Try Pinterest Unauth Resource API
    match = re.search(r"/pin/(?:[\w-]+--)?(\d+)", resolved_url)
    if match:
        pin_id = match.group(1)
        api_url = "https://www.pinterest.com/resource/PinResource/get/"
        headers = {
            "X-Pinterest-PWS-Handler": "www/[username].js",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        }
        params = {
            "data": (
                '{"options":{"field_set_key":"unauth_react_main_pin","id":"'
                + pin_id
                + '"}}'
            )
        }
        try:
            resp = requests.get(api_url, params=params, headers=headers, timeout=15)
            if resp.status_code == 200:
                data = resp.json().get("resource_response", {}).get("data", {})
                title = data.get("title") or data.get("grid_title") or ""

                # Check if pin has video
                videos = data.get("videos")
                if videos and isinstance(videos, dict) and videos.get("video_list"):
                    video_list = videos.get("video_list", {})
                    best_video_url = None
                    max_height = 0
                    for _, vinfo in video_list.items():
                        if isinstance(vinfo, dict) and vinfo.get("url"):
                            h = vinfo.get("height") or 0
                            if h >= max_height:
                                max_height = h
                                best_video_url = vinfo.get("url")
                    if best_video_url:
                        path = download_file_from_url(best_video_url, ext="mp4")
                        return [MediaItem(media_type="video", file_path=path, caption=title)]

                # Check if pin has image
                images = data.get("images", {})
                if images:
                    orig = (
                        images.get("orig")
                        or images.get("736x")
                        or images.get("564x")
                        or list(images.values())[-1]
                    )
                    img_url = orig.get("url") if isinstance(orig, dict) else None
                    if img_url:
                        path = download_file_from_url(img_url, ext="jpg")
                        return [MediaItem(media_type="photo", file_path=path, caption=title)]
        except Exception:
            pass  # Fall through to yt-dlp generic fallback

    # Fallback to generic yt-dlp
    return _download_generic(resolved_url)


def _download_instagram(url: str) -> list[MediaItem]:
    """Download Instagram post (single photo, single video/reel, or carousel)."""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
    }
    if INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD:
        ydl_opts["username"] = INSTAGRAM_USERNAME
        ydl_opts["password"] = INSTAGRAM_PASSWORD

    # Extract metadata without downloading first
    info = None
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False, process=False)
    except Exception as e:
        raise DownloadError(f"Failed to inspect Instagram post: {e}") from e

    if not info:
        raise DownloadError("No media information found for this Instagram post.")

    items: list[MediaItem] = []

    # Case 1: Carousel (playlist)
    if info.get("_type") == "playlist":
        entries = info.get("entries", [])
        for entry in entries:
            formats = entry.get("formats")
            if formats:
                # Video item in carousel
                best_fmt = formats[-1]
                video_url = best_fmt.get("url")
                if video_url:
                    path = download_file_from_url(video_url, ext="mp4")
                    items.append(MediaItem(media_type="video", file_path=path))
            else:
                # Photo item in carousel
                thumbs = entry.get("thumbnails", [])
                if thumbs:
                    best_thumb = thumbs[-1]
                    thumb_url = best_thumb.get("url")
                    if thumb_url:
                        path = download_file_from_url(thumb_url, ext="jpg")
                        items.append(MediaItem(media_type="photo", file_path=path))

    # Case 2: Single item (photo or video)
    else:
        formats = info.get("formats")
        if formats:
            # Single video / Reel: Use yt-dlp to download and merge properly
            try:
                video_path = _download_video_with_ytdlp(url)
                items.append(MediaItem(media_type="video", file_path=video_path))
            except Exception:
                # Fallback to direct stream download if yt-dlp full download failed
                best_fmt = formats[-1]
                video_url = best_fmt.get("url")
                if video_url:
                    path = download_file_from_url(video_url, ext="mp4")
                    items.append(MediaItem(media_type="video", file_path=path))
                else:
                    raise
        else:
            # Single photo post
            thumbs = info.get("thumbnails", [])
            if thumbs:
                best_thumb = thumbs[-1]
                thumb_url = best_thumb.get("url")
                if thumb_url:
                    path = download_file_from_url(thumb_url, ext="jpg")
                    items.append(MediaItem(media_type="photo", file_path=path))

    if not items:
        raise DownloadError("Could not extract any media from this Instagram post.")

    return items


def _download_video_with_ytdlp(url: str) -> str:
    """Download single video using yt-dlp."""
    file_id = str(uuid.uuid4())
    output_template = os.path.join(DOWNLOADS_DIR, f"{file_id}.%(ext)s")

    ydl_opts = {
        "outtmpl": output_template,
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "max_filesize": MAX_VIDEO_SIZE_MB * 1024 * 1024,
    }

    cookies_path = _get_cookies_path()
    if cookies_path:
        ydl_opts["cookiefile"] = cookies_path

    if detect_platform(url) == "Instagram" and INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD:
        ydl_opts["username"] = INSTAGRAM_USERNAME
        ydl_opts["password"] = INSTAGRAM_PASSWORD

    if FFMPEG_PATH:
        ydl_opts["ffmpeg_location"] = FFMPEG_PATH

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            if not os.path.exists(file_path):
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


def _download_generic(url: str) -> list[MediaItem]:
    """Download video or image using generic yt-dlp."""
    try:
        file_path = _download_video_with_ytdlp(url)
        return [MediaItem(media_type="video", file_path=file_path)]
    except DownloadError as e:
        # Check if it was an image post on a generic platform
        try:
            ydl_opts = {"quiet": True, "no_warnings": True}
            cookies_path = _get_cookies_path()
            if cookies_path:
                ydl_opts["cookiefile"] = cookies_path
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False, process=False)
                thumbs = info.get("thumbnails", [])
                if thumbs:
                    best_thumb = thumbs[-1]
                    if best_thumb.get("url"):
                        path = download_file_from_url(best_thumb["url"], ext="jpg")
                        return [MediaItem(media_type="photo", file_path=path)]
        except Exception:
            pass
        raise e


def download_media(url: str) -> list[MediaItem]:
    """
    Download media (photos, videos, carousels, audio) from supported platforms.
    Returns a list of MediaItem objects.
    Raises DownloadError on failure.
    """
    url = normalize_url(url)
    platform = detect_platform(url)

    # 1. Dedicated platforms handled directly by universalDownloader
    universal_first = {
        "Threads",
        "Spotify",
        "Snapchat",
        "CapCut",
        "TeraBox",
        "Douyin",
        "Kuaishou",
        "Bluesky",
        "SoundCloud",
    }
    if platform in universal_first:
        try:
            resp = call_universal_downloader(url)
            if resp:
                u_items = parse_and_download_universal(resp)
                if u_items:
                    return [
                        MediaItem(media_type=it.media_type, file_path=it.file_path, caption=it.caption)
                        for it in u_items
                    ]
        except Exception:
            pass

    # 2. Pinterest (high-res API + fallback)
    if platform == "Pinterest":
        try:
            return _download_pinterest(url)
        except Exception:
            pass

    # 3. Instagram - Primary: universalDownloader, Fallback: yt-dlp
    if platform == "Instagram":
        # First choice: universalDownloader (Snapsave)
        try:
            resp = call_universal_downloader(url, "meta")
            if resp:
                u_items = parse_and_download_universal(resp)
                if u_items:
                    return [
                        MediaItem(media_type=it.media_type, file_path=it.file_path, caption=it.caption)
                        for it in u_items
                    ]
        except Exception:
            pass

        # Fallback choice: yt-dlp patched extractor
        try:
            return _download_instagram(url)
        except Exception:
            pass

    # 4. Generic download using yt-dlp
    try:
        return _download_generic(url)
    except Exception as e:
        # Final fallback: try universalDownloader engine
        try:
            resp = call_universal_downloader(url)
            if resp:
                u_items = parse_and_download_universal(resp)
                if u_items:
                    return [
                        MediaItem(media_type=it.media_type, file_path=it.file_path, caption=it.caption)
                        for it in u_items
                    ]
        except Exception:
            pass
        raise e


def download_video(url: str) -> str:
    """
    Legacy wrapper: Download a video and return its local file path.
    Raises DownloadError on failure.
    """
    items = download_media(url)
    if not items:
        raise DownloadError("No media found.")
    return items[0].file_path


def cleanup_file(file_path: str) -> None:
    """Remove a downloaded file if it exists."""
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except OSError:
        pass


def cleanup_media(items: list[MediaItem]) -> None:
    """Remove all files associated with a list of MediaItems."""
    for item in items:
        cleanup_file(item.file_path)
