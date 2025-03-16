import hashlib

from dandy.core.cache.exceptions import CacheCriticalException


def generate_hash_key(func: object, *args, **kwargs) -> str:
    hashable_args = tuple([convert_to_hashable_str(arg) for arg in args])

    hashable_kwargs = tuple(
        sorted(
            (key, convert_to_hashable_str(value)) for key, value in kwargs.items()
        )
    )

    hashable_tuple = (
        func.__module__,
        func.__qualname__,
        hashable_args,
        hashable_kwargs,
    )

    hash_key = hashlib.sha256(
        str(hashable_tuple).encode()
    ).hexdigest()

    return hash_key


def convert_to_hashable_str(obj: object) -> str:
    if hasattr(obj, '__dict__'):
        return f'{obj.__dict__}'
    elif hasattr(obj, '__str__'):
        return str(obj)
    else:
        raise CacheCriticalException(f'Object "{obj}" is not hashable')
