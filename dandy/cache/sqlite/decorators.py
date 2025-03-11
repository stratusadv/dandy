from dandy.cache.decorators import base_cache_decorator
from dandy.cache.sqlite.cache import SqliteCache


def cache_to_sqlite(name='dandy'):
    def decorator(func):
        return base_cache_decorator(
            SqliteCache(db_name=f'{name}_cache.db')
        )(func)

    return decorator