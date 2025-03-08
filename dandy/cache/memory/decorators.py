from dandy.cache.decorators import base_cache_decorator
from dandy.cache.memory.cache import memory_cache


def cache_to_memory(func):
    return base_cache_decorator(memory_cache)(func)
