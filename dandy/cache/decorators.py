from functools import wraps

from dandy.cache.cache import BaseCache
from dandy.cache.utils import generate_hash_key


def base_cache_decorator(cache: BaseCache):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = generate_hash_key(
                func,
                *args,
                **kwargs
            )

            cached_value = cache.get(key)

            if cached_value:
                return cached_value

            value = func(*args, **kwargs)

            cache.set(key, value)

            return value

        return wrapper

    return decorator
