from dandy.cache.memory.cache import MemoryCache
from dandy.cache.sqlite.cache import SqliteCache

CACHE_LIMIT = 100

sql_lite_cache = SqliteCache(
    cache_name='dandy',
    limit=CACHE_LIMIT
)

memory_cache = MemoryCache(
    cache_name='dandy',
    limit=CACHE_LIMIT
)


