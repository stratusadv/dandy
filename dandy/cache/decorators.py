from dandy.cache.cache import BaseCache
from dandy.cache.utils import generate_hash_key
from dandy.intel import BaseIntel
from dandy.recorder import Recorder
from dandy.recorder.events import Event, EventAttribute, EventType
from dandy.recorder.utils import generate_new_recorder_event_id


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

    cache.set(hash_key, value)

    return value
