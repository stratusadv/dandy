from functools import wraps
from typing import Callable

import dandy.consts
from dandy.cache.decorators import cache_decorator_function
from dandy.cache.memory.cache import MemoryCache
from dandy.conf import settings


def cache_to_memory(
        cache_name: str = dandy.consts.DEFAULT_CACHE_NAME,
        limit: int = settings.CACHE_MEMORY_LIMIT
) -> Callable:
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return cache_decorator_function(
                MemoryCache(
                    cache_name=cache_name,
                    limit=limit
                ),
                func,
                *args,
                **kwargs
            )

        return wrapper

    return decorator
