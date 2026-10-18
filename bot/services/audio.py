"""
Audio extraction from video using FFmpeg.
"""
import os
import uuid
import subprocess
from bot.config import MEDIA_DIR, FFMPEG_PATH

import shutil

try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except Exception:
    pass


def get_ffmpeg_bin() -> str:
    """Return a working path to ffmpeg executable, validating existence."""
    if FFMPEG_PATH and os.path.exists(FFMPEG_PATH):
        return FFMPEG_PATH

    cand = shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")
    if cand:
        return cand

    try:
        import static_ffmpeg
        static_ffmpeg.add_paths()
        cand = shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")
        if cand:
            return cand
    except Exception:
        pass

    return "ffmpeg"


FFMPEG_BIN = get_ffmpeg_bin()



class AudioExtractionError(Exception):
    """Raised when audio extraction fails."""


def extract_audio(video_path: str, duration_seconds: int = 20) -> str:
    """
    Extract a short audio clip (mono, 16kHz WAV) from a video file for
    music recognition. Returns the path to the generated audio file.
    """
    audio_path = os.path.join(MEDIA_DIR, f"{uuid.uuid4()}.wav")

    command = [
        FFMPEG_BIN,
        "-y",
        "-i", video_path,
        "-t", str(duration_seconds),
        "-vn",
        "-ac", "1",
        "-ar", "16000",
        "-f", "wav",
        audio_path,
    ]

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60,
        )
        if result.returncode != 0 or not os.path.exists(audio_path):
            raise AudioExtractionError(result.stderr.decode(errors="ignore"))
        return audio_path
    except subprocess.TimeoutExpired as e:
        raise AudioExtractionError("FFmpeg timed out.") from e


def extract_full_audio(
    video_path: str,
    title: str | None = None,
    artist: str | None = None,
) -> str:
    """
    Extract the full audio from a video file as MP3.
    Returns the path to the generated MP3 file.
    """
    audio_path = os.path.join(MEDIA_DIR, f"{uuid.uuid4()}.mp3")

    command = [
        FFMPEG_BIN,
        "-y",
        "-i", video_path,
        "-vn",
        "-c:a", "libmp3lame",
        "-q:a", "2",
    ]
    if title:
        command.extend(["-metadata", f"title={title}"])
    if artist:
        command.extend(["-metadata", f"artist={artist}"])
    command.append(audio_path)

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=180,
        )
        if result.returncode != 0 or not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
            raise AudioExtractionError(result.stderr.decode(errors="ignore"))
        return audio_path
    except subprocess.TimeoutExpired as e:
        raise AudioExtractionError("FFmpeg timed out while extracting full audio.") from e


def cleanup_file(file_path: str) -> None:
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except OSError:
        pass


def download_audio_by_query(query: str) -> str | None:
    """
    Search and download a full studio track as MP3 using yt-dlp.
    Returns the path to the downloaded MP3 file or None on failure.
    """
    import yt_dlp
    from bot.config import DOWNLOADS_DIR

    file_id = str(uuid.uuid4())
    output_template = os.path.join(DOWNLOADS_DIR, f"{file_id}.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "max_filesize": 40 * 1024 * 1024,
    }
    if FFMPEG_PATH:
        ydl_opts["ffmpeg_location"] = FFMPEG_PATH

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query} audio", download=True)
            if not info or not info.get("entries"):
                return None
            expected_mp3 = os.path.join(DOWNLOADS_DIR, f"{file_id}.mp3")
            if os.path.exists(expected_mp3):
                return expected_mp3
            for ext in (".mp3", ".m4a", ".opus", ".webm"):
                cand = os.path.join(DOWNLOADS_DIR, f"{file_id}{ext}")
                if os.path.exists(cand):
                    return cand
            return None
    except Exception:
        return None

