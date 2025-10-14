from typing import OrderedDict, Any

import dandy.consts
from dandy.cache.cache import BaseCache

_memory_cache = {}


class MemoryCache(BaseCache):
    cache_name: str
    limit: int

    @property
    def _cache(self) -> OrderedDict:
        if self.cache_name not in _memory_cache:
            _memory_cache[self.cache_name] = OrderedDict()

        return _memory_cache[self.cache_name]

    def __len__(self) -> int:
        return len(self._cache)

    def get(self, key: str) -> Any | None:
        return self._cache.get(key)

    def set(self, key: str, value: Any):
        self._cache[key] = value
        self.clean()

    def clean(self):
        if len(self._cache) > self.limit:
            self._cache.popitem(last=False)

    @classmethod
    def clear(cls, cache_name: str = dandy.consts.CACHE_DEFAULT_NAME):
        if cache_name in _memory_cache:
            _memory_cache[cache_name].clear()

    @classmethod
    def clear_all(cls):
        _memory_cache.clear()

    @classmethod
    def destroy_all(cls):
        cls.clear_all()
