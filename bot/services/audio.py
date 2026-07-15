"""
Audio extraction from video using FFmpeg.
"""
import os
import uuid
import subprocess
from bot.config import MEDIA_DIR, FFMPEG_PATH

FFMPEG_BIN = FFMPEG_PATH if FFMPEG_PATH else "ffmpeg"


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


def cleanup_file(file_path: str) -> None:
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except OSError:
        pass
