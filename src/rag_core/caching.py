import hashlib
import json
import logging
import time
from typing import Any

import redis

logger = logging.getLogger(__name__)


class TwoLevelCache:
    """
    Двухуровневый кэш:
    1) In-memory словарь для быстрых повторных запросов в рамках процесса.
    2) Redis для долговременного хранения между процессами/хостами.
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        ttl: int = 300,
        namespace: str = "rag_cache:",
    ):
        self.ttl = ttl
        self.namespace = namespace
        self.memory_store: dict[str, tuple[Any, float]] = {}
        self.redis = redis.Redis.from_url(redis_url, decode_responses=True)

    def _now(self) -> float:
        return time.time()

    def _make_key(self, data: str) -> str:
        """Генерация стабильного хэша для ключа."""
        digest = hashlib.sha256(data.encode("utf-8")).hexdigest()
        return f"{self.namespace}{digest}"

    def get(self, raw_key: str) -> Any | None:
        key = self._make_key(raw_key)

        # 1. Память
        value_ttl = self.memory_store.get(key)
        if value_ttl:
            value, expires = value_ttl
            if expires > self._now():
                logger.debug(f"[CACHE] Memory hit for {raw_key}")
                return value
            else:
                self.memory_store.pop(key, None)

        # 2. Redis
        try:
            data = self.redis.get(key)
            if data is not None:
                logger.debug(f"[CACHE] Redis hit for {raw_key}")
                value = json.loads(data)
                self.memory_store[key] = (value, self._now() + self.ttl)
                return value
        except Exception as e:
            logger.warning(f"[CACHE] Redis error: {e}")

        logger.debug(f"[CACHE] Miss for {raw_key}")
        return None

    def set(self, raw_key: str, value: Any) -> None:
        key = self._make_key(raw_key)
        expires = self._now() + self.ttl

        # Память
        self.memory_store[key] = (value, expires)

        # Redis
        try:
            self.redis.setex(key, self.ttl, json.dumps(value))
        except Exception as e:
            logger.warning(f"[CACHE] Redis set error: {e}")

    def invalidate(self, raw_key: str) -> None:
        key = self._make_key(raw_key)
        self.memory_store.pop(key, None)
        try:
            self.redis.delete(key)
        except Exception as e:
            logger.warning(f"[CACHE] Redis delete error: {e}")
