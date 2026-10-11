"""
Integration bridge for universalDownloader (Node.js engine).
Provides access to Threads, Spotify, Snapchat, CapCut, TeraBox, Douyin,
Kuaishou, Bluesky, SoundCloud, Reddit, Tumblr, LinkedIn and more.
"""
import json
import logging
import os
import subprocess
from dataclasses import dataclass
from typing import Literal

from bot.config import BASE_DIR, DOWNLOADS_DIR, MAX_VIDEO_SIZE_MB

logger = logging.getLogger(__name__)

CLI_PATH = os.path.join(BASE_DIR, "universalDownloader", "cli.js")


@dataclass
class UniversalMediaItem:
    media_type: Literal["video", "photo", "audio"]
    file_path: str
    caption: str = ""


def is_node_available() -> bool:
    """Check if Node.js is installed on the host system."""
    try:
        subprocess.run(
            ["node", "-v"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            timeout=5,
        )
        return True
    except Exception:
        return False


def call_universal_downloader(url: str, platform: str | None = None) -> dict | None:
    """
    Execute universalDownloader/cli.js using Node.js and return parsed JSON data.
    """
    if not os.path.exists(CLI_PATH):
        logger.warning("universalDownloader cli.js not found at %s", CLI_PATH)
        return None

    cmd = ["node", CLI_PATH, url]
    if platform:
        cmd.append(platform)

    try:
        proc = subprocess.run(
            cmd,
            cwd=os.path.dirname(CLI_PATH),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=40,
        )
        if proc.returncode == 0 and proc.stdout:
            data = json.loads(proc.stdout.strip())
            if data.get("success"):
                return data
        else:
            logger.warning("universalDownloader failed (code %s): %s", proc.returncode, proc.stderr)
            return None
    except Exception as e:
        logger.error("Error executing universalDownloader: %s", e)
        return None


def download_remote_file(
    url: str,
    preferred_ext: str | None = None,
    preferred_type: Literal["video", "photo", "audio"] | None = None,
) -> tuple[str, Literal["video", "photo", "audio"]]:
    """Download a direct remote file to the downloads directory with automatic Content-Type detection."""
    import uuid
    import requests

    file_id = str(uuid.uuid4())
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers, stream=True, timeout=35)
    resp.raise_for_status()

    # Detect media type from Content-Type header or URL
    content_type = (resp.headers.get("content-type") or "").lower()
    media_type: Literal["video", "photo", "audio"] = preferred_type or "video"
    ext = preferred_ext or "mp4"

    if "image/" in content_type:
        media_type = "photo"
        ext = "jpg"
    elif "audio/" in content_type:
        media_type = "audio"
        ext = "mp3"
    elif "video/" in content_type:
        media_type = "video"
        ext = "mp4"
    elif any(x in url.lower() for x in (".jpg", ".jpeg", ".png", ".webp")):
        media_type = "photo"
        ext = "jpg"
    elif any(x in url.lower() for x in (".mp3", ".m4a", ".ogg")):
        media_type = "audio"
        ext = "mp3"

    file_path = os.path.join(DOWNLOADS_DIR, f"{file_id}.{ext}")
    max_bytes = MAX_VIDEO_SIZE_MB * 1024 * 1024
    total_bytes = 0

    with open(file_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                total_bytes += len(chunk)
                if total_bytes > max_bytes:
                    raise Exception(f"File exceeds maximum size of {MAX_VIDEO_SIZE_MB}MB.")
                f.write(chunk)

    # Magic bytes check for guaranteed accurate media type detection
    try:
        with open(file_path, "rb") as f:
            head = f.read(32)

        detected_type = media_type
        new_ext = ext

        if head.startswith(b"\xff\xd8\xff") or head.startswith(b"\x89PNG") or (head.startswith(b"RIFF") and b"WEBP" in head):
            detected_type = "photo"
            new_ext = "jpg"
        elif b"ftyp" in head or head.startswith(b"\x1aE\xdf\xa3") or b"moov" in head or head.startswith(b"\x00\x00\x00"):
            detected_type = "video"
            new_ext = "mp4"
        elif head.startswith(b"ID3") or head.startswith(b"\xff\xfb") or head.startswith(b"OggS") or head.startswith(b"fLaC"):
            detected_type = "audio"
            new_ext = "mp3"

        if new_ext != ext:
            new_path = file_path.rsplit(".", 1)[0] + f".{new_ext}"
            if os.path.exists(new_path):
                os.remove(new_path)
            os.rename(file_path, new_path)
            file_path = new_path
            media_type = detected_type
    except Exception:
        pass

    return file_path, media_type


def parse_and_download_universal(resp_data: dict) -> list[UniversalMediaItem]:
    """
    Parse the JSON result returned by universalDownloader and download the actual media files.
    """
    platform = resp_data.get("platform", "").lower()
    data = resp_data.get("data", {})
    items: list[UniversalMediaItem] = []

    if not data:
        return items

    # 1. Meta (Instagram & Facebook via Snapsave)
    if platform in ("meta", "instagram", "facebook"):
        items_list = []
        if isinstance(data, dict):
            if isinstance(data.get("data"), list):
                items_list = data["data"]
            elif isinstance(data.get("media"), list):
                items_list = data["media"]
            elif data.get("url"):
                items_list = [data]
        elif isinstance(data, list):
            items_list = data

        for entry in items_list:
            if not isinstance(entry, dict):
                continue
            media_url = entry.get("url") or entry.get("download_url") or entry.get("video")
            if not media_url:
                continue

            try:
                fpath, mtype = download_remote_file(media_url)
                items.append(UniversalMediaItem(media_type=mtype, file_path=fpath))
            except Exception as e:
                logger.warning("Failed to download Meta item: %s", e)

    # 2. Threads
    elif platform == "threads":
        # Photos
        for photo in data.get("photos", []):
            variants = photo.get("variants", [])
            img_url = variants[0].get("url") if variants else photo.get("thumbnail")
            if img_url:
                try:
                    fpath, mtype = download_remote_file(img_url, preferred_ext="jpg", preferred_type="photo")
                    items.append(UniversalMediaItem(media_type=mtype, file_path=fpath))
                except Exception as e:
                    logger.warning("Failed to download Threads photo: %s", e)
        # Videos
        for video in data.get("videos", []):
            v_url = video.get("url")
            if v_url:
                try:
                    fpath, mtype = download_remote_file(v_url, preferred_ext="mp4", preferred_type="video")
                    items.append(UniversalMediaItem(media_type=mtype, file_path=fpath))
                except Exception as e:
                    logger.warning("Failed to download Threads video: %s", e)

    # 3. Bluesky
    elif platform == "bluesky":
        caption = data.get("caption") or ""
        for photo in data.get("photos", []):
            p_url = photo.get("url") or photo.get("thumbnail")
            if p_url:
                try:
                    fpath, mtype = download_remote_file(p_url, preferred_ext="jpg", preferred_type="photo")
                    items.append(UniversalMediaItem(media_type=mtype, file_path=fpath, caption=caption))
                except Exception:
                    pass
        for video in data.get("videos", []):
            v_url = video.get("url")
            if v_url:
                try:
                    fpath, mtype = download_remote_file(v_url, preferred_ext="mp4", preferred_type="video")
                    items.append(UniversalMediaItem(media_type=mtype, file_path=fpath, caption=caption))
                except Exception:
                    pass

    # 4. Douyin
    elif platform == "douyin":
        title = data.get("title") or ""
        links = data.get("links", [])
        if links:
            v_url = links[0].get("url")
            if v_url:
                try:
                    fpath, mtype = download_remote_file(v_url, preferred_ext="mp4", preferred_type="video")
                    items.append(UniversalMediaItem(media_type=mtype, file_path=fpath, caption=title))
                except Exception:
                    pass

    # 5. CapCut
    elif platform == "capcut":
        title = data.get("title") or ""
        v_url = data.get("video_url") or data.get("url") or data.get("download_url") or data.get("media_url")
        if v_url:
            try:
                fpath, mtype = download_remote_file(v_url, preferred_ext="mp4", preferred_type="video")
                items.append(UniversalMediaItem(media_type=mtype, file_path=fpath, caption=title))
            except Exception:
                pass

    # 6. Snapchat
    elif platform == "snapchat":
        v_url = data.get("video_url") or data.get("url") or data.get("download_url")
        if v_url:
            try:
                fpath, mtype = download_remote_file(v_url, preferred_ext="mp4", preferred_type="video")
                items.append(UniversalMediaItem(media_type=mtype, file_path=fpath))
            except Exception:
                pass

    # 7. Spotify
    elif platform == "spotify":
        title = data.get("title") or data.get("songTitle") or "Spotify Track"
        artist = data.get("artist") or ""
        caption = f"🎵 {title} - {artist}" if artist else f"🎵 {title}"
        audio_url = data.get("downloadUrl") or data.get("url") or data.get("audio") or data.get("link")
        if audio_url:
            try:
                fpath, mtype = download_remote_file(audio_url, preferred_ext="mp3", preferred_type="audio")
                items.append(UniversalMediaItem(media_type=mtype, file_path=fpath, caption=caption))
            except Exception:
                pass

    # 8. TeraBox
    elif platform == "terabox":
        v_url = data.get("download_link") or data.get("fast_download_link") or data.get("url")
        if v_url:
            try:
                fpath, mtype = download_remote_file(v_url, preferred_ext="mp4", preferred_type="video")
                items.append(UniversalMediaItem(media_type=mtype, file_path=fpath))
            except Exception:
                pass

    # 9. TikTok (SSSTik fallback)
    elif platform == "tiktok":
        title = data.get("title") or ""
        downloads = data.get("downloads", [])
        for dl in downloads:
            url_dl = dl.get("url")
            if url_dl and (".mp4" in url_dl.lower() or "video" in dl.get("text", "").lower() or not dl.get("text")):
                try:
                    fpath, mtype = download_remote_file(url_dl, preferred_ext="mp4", preferred_type="video")
                    items.append(UniversalMediaItem(media_type=mtype, file_path=fpath, caption=title))
                    break
                except Exception:
                    pass

    # 10. Generic fallback: check common URL fields
    if not items:
        url_candidates = []
        if isinstance(data, dict):
            for k in ("url", "download_url", "video_url", "media_url", "direct_url", "video"):
                if data.get(k) and isinstance(data[k], str) and data[k].startswith("http"):
                    url_candidates.append(data[k])
            if "downloads" in data and isinstance(data["downloads"], list):
                for d in data["downloads"]:
                    if isinstance(d, dict) and d.get("url"):
                        url_candidates.append(d["url"])

        for cand in url_candidates:
            try:
                fpath, mtype = download_remote_file(cand)
                items.append(UniversalMediaItem(media_type=mtype, file_path=fpath))
                break
            except Exception:
                pass

    return items
