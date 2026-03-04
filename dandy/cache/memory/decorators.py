from functools import wraps
from typing import Callable

from dandy.cache.decorators import cache_decorator_function
from dandy.cache.memory.cache import MemoryCache
from dandy.conf import settings
from dandy.constants import CACHE_DEFAULT_NAME


def cache_to_memory(
        cache_name: str = CACHE_DEFAULT_NAME,
        limit: int | None = None,
) -> Callable:
    if limit is None:
        limit = settings.CACHE_MEMORY_LIMIT

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Callable:
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
