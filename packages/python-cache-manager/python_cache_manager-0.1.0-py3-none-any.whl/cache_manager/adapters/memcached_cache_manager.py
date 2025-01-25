# my_cache_manager/memcached_cache_manager.py

from pymemcache.client.base import Client
import json
from typing import Any, Optional
from ..cache_manager import BaseCacheManager


class MemcacheException(Exception):
    pass


class MemcachedCacheManager(BaseCacheManager):
    def __init__(self, host: str = 'localhost', port: int = 11211):
        self.host = host
        self.port = port
        self.mc = Client((host, port), serializer=self.json_serializer,
                         deserializer=self.json_deserializer, timeout=5, connect_timeout=5)

    def json_serializer(self, key: str, value: Any) -> tuple:
        if type(value) == str:
            return value, 1
        return json.dumps(value), 2

    def json_deserializer(self, key: str, value: Any, flags: int) -> Any:
        if flags == 1:
            return value.decode('utf-8')
        if flags == 2:
            return json.loads(value.decode('utf-8'))
        else:
            return json.loads(value.decode('utf-8'))

    def get_many_from_cache(self, key_list: list) -> dict:
        return self.mc.get_many(key_list)

    def add_many_to_cache(self, items: Any, expire_duration: Optional[int] = 3600):
        if self.mc.set_many(items, expire=expire_duration) == 0:
            raise MemcacheException("Failed to add items to cache")

    def delete(self, key: str) -> bool:
        if self.mc.delete(key) == 0:
            raise MemcacheException("Failed to delete item from cache")
        return True

    def set(self, key: str, value: Any, ttl: Optional[int] = 3600) -> bool:
        if self.mc.set(key, value, expire=ttl) == 0:
            # to reconnect
            self.mc = Client((self.host, self.port), serializer=self.json_serializer,
                             deserializer=self.json_deserializer)

            if self.mc.set(key, value, expire=ttl) == 0:
                raise MemcacheException("Failed to add item to cache")

    def get(self, key: str) -> Optional[Any]:
        val = self.mc.get(key)
        return val

    def clear(self) -> bool:
        self.mc.flush_all()
        return True
