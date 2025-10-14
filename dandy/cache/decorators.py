from typing import Any, Callable

from dandy.cache.cache import BaseCache
from dandy.cache.tools import generate_cache_key
from dandy.intel.intel import BaseIntel
from dandy.recorder import Recorder
from dandy.recorder.events import Event, EventAttribute, EventType
from dandy.recorder.utils import generate_new_recorder_event_id


def cache_decorator_function(
        cache: BaseCache,
        func: Callable,
        *args,
        **kwargs,
) -> Any:
    cache_key = generate_cache_key(
        func,
        *args,
        **kwargs
    )

    cached_value = cache.get(cache_key)

    if cached_value:
        if Recorder.is_recording:
            if isinstance(cached_value, BaseIntel):
                response = cached_value.model_dump_json(indent=4)
            else:
                response = str(cached_value)

            Recorder.add_event(
                Event(
                    id=generate_new_recorder_event_id(),
                    object_name='Cache',
                    callable_name='Response',
                    type=EventType.RESPONSE,
                    attributes=[
                        EventAttribute(
                            key='Cached Response',
                            value=response,
                        ),
                    ],
                )
            )

        return cached_value

    value = func(*args, **kwargs)

    cache.set(cache_key, value)

    return value
