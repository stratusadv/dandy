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
    hashable_string = str(None)

    if hash_layer <= CACHE_KEY_HASH_LAYER_LIMIT:
        try:
            if isinstance(obj, type):
                if issubclass(obj, BaseModel):
                    hashable_string= str(obj.model_json_schema())
                else:
                    hashable_string= str(obj.__qualname__)

            elif isinstance(obj, BaseModel):
                hashable_string= str(obj.model_dump())

            elif isinstance(obj, dict):
                hashable_string= str({
                    key: convert_to_hashable_str(value, hash_layer + 1) for key, value in obj.items()
                })

            elif isinstance(obj, (list, tuple, set, frozenset)):
                hashable_string= str([
                    convert_to_hashable_str(x, hash_layer + 1) for x in obj
                ])

            elif hasattr(obj, '__dict__'):
                hashable_string= convert_to_hashable_str(obj.__dict__, hash_layer + 1)

            else:
                hashable_string= str(obj)

        except TypeError as error:
            message = f'Object "{obj}" is not hashable'
            raise CacheCriticalException(message) from error

    return hashable_string
