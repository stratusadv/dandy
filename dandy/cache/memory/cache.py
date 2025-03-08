from typing_extensions import OrderedDict, Union, Any

from dandy.cache.cache import BaseCache


class MemoryCache(BaseCache):
    _cache: OrderedDict = OrderedDict()
    limit: int = 1000

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


memory_cache = MemoryCache()