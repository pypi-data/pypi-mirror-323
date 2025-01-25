# my_cache_manager/cache_manager_factory.py

import os
from .adapters.redis_cache_manager import RedisCacheManager
from .adapters.memcached_cache_manager import MemcachedCacheManager


class CacheManagerFactory:
    _cache_manager_instance = None

    @classmethod
    def get_cache_manager(cls, backend: str = None, host: str = None, port: int = None):
        # Return the existing instance if it already exists
        if cls._cache_manager_instance is not None:
            return cls._cache_manager_instance

        # Fetch parameters from environment variables or default values
        backend = backend or os.getenv('CACHE_BACKEND', 'redis')
        host = host or os.getenv('CACHE_HOST', 'localhost')
        port = port or int(
            os.getenv('CACHE_PORT', 6379 if backend == 'redis' else 11211))

        if backend.lower() == 'redis':
            password = os.getenv('CACHE_PASSWORD', "")
            db = int(os.getenv('CACHE_DB', 0))
            cls._cache_manager_instance = RedisCacheManager(
                host=host, port=port, password=password, db=db)
        elif backend.lower() == 'memcache':
            cls._cache_manager_instance = MemcachedCacheManager(
                host=host, port=port)
        else:
            raise ValueError(f"Unsupported backend: {backend}")
        return cls._cache_manager_instance
