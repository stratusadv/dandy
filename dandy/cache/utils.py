import hashlib

from pydantic import BaseModel
from typing import Any

from dandy.cache.exceptions import CacheCriticalException
from dandy.consts import CACHE_KEY_HASH_LAYER_LIMIT


def generate_cache_key(func: object, *args, **kwargs) -> str:
    hashable_args = tuple(
        convert_to_hashable_str(arg) for arg in args
    )

    hashable_kwargs = tuple(
        (key, convert_to_hashable_str(value)) for key, value in kwargs.items()
    )

    hashable_tuple = (
        func.__module__,
        func.__qualname__,
        hashable_args,
        hashable_kwargs,
    )

    hash_key = hashlib.shake_128(
        str(hashable_tuple).encode()
    ).hexdigest(16)

    return hash_key


def convert_to_hashable_str(obj: Any, hash_layer: int = 1) -> str:
    if hash_layer <= CACHE_KEY_HASH_LAYER_LIMIT:
        if isinstance(obj, type):
            if issubclass(obj, BaseModel):
                return str(obj.model_json_schema())
            else:
                return str(obj.__qualname__)
        elif isinstance(obj, BaseModel):
            return str(obj.model_dump())
        elif isinstance(obj, dict):
            return str({
                key: convert_to_hashable_str(value, hash_layer + 1) for key, value in obj.items()
            })
        elif isinstance(obj, (list, tuple, set, frozenset)):
            return str([
                convert_to_hashable_str(x, hash_layer + 1) for x in obj
            ])
        elif hasattr(obj, '__dict__'):
            return convert_to_hashable_str(obj.__dict__, hash_layer + 1)

        try:
            return str(obj)
        except TypeError:
            message = f'Object "{obj}" is not hashable'
            raise CacheCriticalException(message)
    else:
        return str(None)
