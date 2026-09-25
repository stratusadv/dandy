from functools import wraps
from typing import Callable

from dandy.infrastructure.cache.decorators import cache_decorator_function
from dandy.infrastructure.cache.memory.cache import MemoryCache
from dandy.shared.conf import settings
from dandy.shared.constants import CACHE_DEFAULT_NAME


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
