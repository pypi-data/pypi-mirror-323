# my_cache_manager/cache_manager.py

from abc import ABC, abstractmethod
from typing import Any, Optional

class BaseCacheManager(ABC):
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        pass

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        pass

    @abstractmethod
    def clear(self) -> bool:
        pass
