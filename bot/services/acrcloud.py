"""
Music recognition using the ACRCloud Identify API.
Docs: https://docs.acrcloud.com/reference/identify-api
"""
import base64
import hashlib
import hmac
import time
import requests

from bot.config import ACR_HOST, ACR_ACCESS_KEY, ACR_ACCESS_SECRET


class RecognitionResult:
    def __init__(self, title: str, artist: str, album: str | None, score: int):
        self.title = title
        self.artist = artist
        self.album = album
        self.score = score


def _build_signature(timestamp: str) -> str:
    http_method = "POST"
    http_uri = "/v1/identify"
    data_type = "audio"
    signature_version = "1"

    string_to_sign = "\n".join([
        http_method, http_uri, ACR_ACCESS_KEY, data_type, signature_version, timestamp
    ])

    signature = base64.b64encode(
        hmac.new(
            ACR_ACCESS_SECRET.encode("ascii"),
            string_to_sign.encode("ascii"),
            digestmod=hashlib.sha1,
        ).digest()
    ).decode("ascii")

    return signature


def recognize_audio(audio_path: str) -> RecognitionResult | None:
    """
    Send an audio file to ACRCloud for recognition.
    Returns a RecognitionResult, or None if no match was found.
    """
    timestamp = str(time.time())
    signature = _build_signature(timestamp)

    with open(audio_path, "rb") as f:
        sample_bytes = f.read()

    files = {"sample": ("sample.wav", sample_bytes, "audio/wav")}
    data = {
        "access_key": ACR_ACCESS_KEY,
        "sample_bytes": len(sample_bytes),
        "timestamp": timestamp,
        "signature": signature,
        "data_type": "audio",
        "signature_version": "1",
    }

    url = f"https://{ACR_HOST}/v1/identify"
    response = requests.post(url, files=files, data=data, timeout=30)
    result = response.json()

    status = result.get("status", {})
    if status.get("code") != 0:
        return None

    music_list = result.get("metadata", {}).get("music", [])
    if not music_list:
        return None

    top_match = music_list[0]
    title = top_match.get("title", "Unknown")
    artists = ", ".join(a.get("name", "") for a in top_match.get("artists", []))
    album = top_match.get("album", {}).get("name")
    score = top_match.get("score", 0)

    return RecognitionResult(title=title, artist=artists, album=album, score=score)
