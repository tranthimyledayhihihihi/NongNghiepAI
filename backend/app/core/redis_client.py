import json
from typing import Any

from .config import settings

try:
    import redis
except ModuleNotFoundError:  # pragma: no cover - depends on local environment
    redis = None


class RedisClient:
    def __init__(self):
        self.client = redis.from_url(settings.REDIS_URL, decode_responses=True) if redis else None
        self.enabled = self.client is not None

    def _disable(self):
        self.enabled = False
        self.client = None

    def get(self, key: str) -> Any | None:
        if not self.enabled or self.client is None:
            return None
        try:
            value = self.client.get(key)
            return json.loads(value) if value else None
        except Exception:
            self._disable()
            return None

    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        if not self.enabled or self.client is None:
            return False
        try:
            self.client.setex(key, expire, json.dumps(value))
            return True
        except Exception:
            self._disable()
            return False

    def delete(self, key: str) -> bool:
        if not self.enabled or self.client is None:
            return False
        try:
            self.client.delete(key)
            return True
        except Exception:
            self._disable()
            return False


redis_client = RedisClient()
