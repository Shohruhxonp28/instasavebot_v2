import os
import time
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CachedAudio:
    audio_path: str | None
    title: str
    artist: str
    bot_username: str
    file_id: str | None = None
    created_at: float = 0.0


class AudioCache:
    def __init__(self, ttl_seconds: int = 3600):
        self._cache: dict[str, CachedAudio] = {}
        self.ttl = ttl_seconds

    def store(
        self,
        token: str,
        audio_path: str,
        title: str,
        artist: str,
        bot_username: str,
    ) -> None:
        self.cleanup_expired()
        self._cache[token] = CachedAudio(
            audio_path=audio_path,
            title=title,
            artist=artist,
            bot_username=bot_username,
            created_at=time.time(),
        )

    def get(self, token: str) -> CachedAudio | None:
        return self._cache.get(token)

    def cleanup_expired(self) -> None:
        now = time.time()
        expired_keys = [
            k for k, v in self._cache.items() if now - v.created_at > self.ttl
        ]
        for k in expired_keys:
            item = self._cache.pop(k, None)
            if item and item.audio_path and os.path.exists(item.audio_path):
                try:
                    os.remove(item.audio_path)
                except OSError:
                    pass


audio_cache = AudioCache()
