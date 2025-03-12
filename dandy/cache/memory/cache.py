from typing_extensions import OrderedDict, Union, Any

from dandy.cache.cache import BaseCache
from dandy.conf import settings

_memory_cache = dict()


class MemoryCache(BaseCache):
    cache_name: str
    limit: int

    @property
    def _cache(self):
        if self.cache_name not in _memory_cache:
            _memory_cache[self.cache_name] = OrderedDict()

        return _memory_cache[self.cache_name]

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

    @classmethod
    def clear(cls, cache_name: str = settings.DEFAULT_CACHE_NAME):
        if cache_name in _memory_cache:
            _memory_cache[cache_name].clear()

    @classmethod
    def destroy(cls, cache_name: str = settings.DEFAULT_CACHE_NAME):
        cls.clear(cache_name)
