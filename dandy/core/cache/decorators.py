from dandy.core.cache.cache import BaseCache
from dandy.core.cache.events import CacheEvent
from dandy.core.cache.utils import generate_hash_key
from dandy.debug import DebugRecorder
from dandy.debug.utils import generate_new_debug_event_id
from dandy.intel import BaseIntel


def cache_decorator_function(
        cache: BaseCache,
        func,
        *args,
        **kwargs,
):
    hash_key = generate_hash_key(
        func,
        *args,
        **kwargs
    )

    cached_value = cache.get(hash_key)

    if cached_value:
        if DebugRecorder.is_recording:
            if isinstance(cached_value, BaseIntel):
                response = cached_value.model_dump_json(indent=4)
            else:
                response = str(cached_value)

            DebugRecorder.add_event(CacheEvent(
                response=response,
                id=generate_new_debug_event_id()
            ))

        return cached_value

    value = func(*args, **kwargs)

    cache.set(hash_key, value)

    return value
