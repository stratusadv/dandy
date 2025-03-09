from typing_extensions import OrderedDict, Union, Any

from dandy.cache.cache import BaseCache
from dandy.conf import settings


class MemoryCache(BaseCache):
    _cache: OrderedDict = OrderedDict()
    limit: int = settings.CACHE_MEMORY_LIMIT

    def __len__(self) -> int:
        return len(self._cache)

    def get(self, key: str) -> Union[Any, None]:
        return self._cache.get(key)

    def set(self, key: str, value: Any):
        self._cache[key] = value
        self.clean()

    def clean(self):
        if len(self._cache) > self.limit:
            self._cache.popitem(last=False)

    def clear(self):
        self._cache.clear()

    def destroy(self):
        self.clear()


memory_cache = MemoryCache()