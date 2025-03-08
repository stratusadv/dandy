from dandy.cache.decorators import base_cache_decorator
from dandy.cache.sqlite.cache import sqlite_cache


def cache_to_sqlite(func):
    return base_cache_decorator(sqlite_cache)(func)
