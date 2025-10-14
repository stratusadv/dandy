from functools import wraps
from typing import Callable

import dandy.consts
from dandy.cache.decorators import cache_decorator_function
from dandy.cache.sqlite.cache import SqliteCache
from dandy.conf import settings


def cache_to_sqlite(
        cache_name: str = dandy.consts.CACHE_DEFAULT_NAME,
        limit: int = settings.CACHE_SQLITE_LIMIT
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Callable:
            return cache_decorator_function(
                SqliteCache(
                    cache_name=cache_name,
                    limit=limit,
                ),
                func,
                *args,
                **kwargs
            )

        return wrapper

    return decorator
