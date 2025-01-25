# my_cache_manager/redis_cache_manager.py

import redis
import json
from typing import Any, Optional
from ..cache_manager import BaseCacheManager


class RedisCacheManager(BaseCacheManager):
    def __init__(self, host: str = 'localhost', password: str = "", port: int = 6379, db: int = 0):
        self.client = redis.Redis(
            host=host, port=port, db=db, password=password, socket_connect_timeout=2, socket_timeout=10)

    def set(self, key: str, value: Any, ttl: Optional[int] = 3600) -> bool:
        """
        Set a value in the cache, if connection is lost, it tries to reconnect.
        :param key: Cache key
        :param value: Value to store
        :param ttl: Expiry time in seconds. If None, the value never expires.
        """
        set_result = self.client.set(name=key, value=json.dumps(value), ex=ttl)
        if set_result == 0:
            # to reconnect
            self.client = redis.Redis(
                host=self.host, port=self.port, db=self.db, password=self.password)
            if self.client.set(name=key, value=json.dumps(value), ex=ttl) == 0:
                raise Exception("Failed to add item to cache")
        return True

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        :param key: Cache key
        :return: Value if found, else None
        """
        value = self.client.get(name=key)
        if value:
            return True, json.loads(value)
        return False, None

    def delete(self, key: str) -> bool:
        """
        Delete a key from the cache.
        :param key: Cache key
        """
        return self.client.delete(key) > 0

    def exists(self, key) -> bool:
        """
        Check if a key exists in the cache.
        :param key: Cache key
        :return: True if key exists, False otherwise
        """
        try:
            return self.client.exists(key) > 0
        except:
            return False
    
    def clear(self, pattern=None) -> bool:
        """
        Clear the entire cache.
        """
        if pattern:
            return self._clear_with_pattern(pattern)

        try:
            self.client.flushdb()
        except:
            return False

    def _clear_with_pattern(self, pattern):
        """
        Clear the cache with a pattern.
        :param pattern: Pattern to match keys
        """
        try:
            keys = self.client.keys(pattern)
            for key in keys:
                self.client.delete(key)
        except:
            return False
