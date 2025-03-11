import hashlib


def generate_hash_key(func: object, *args, **kwargs) -> str:
    hashable_tuple = (
        func.__module__,
        func.__qualname__,
        args,
        tuple(sorted(kwargs.items()))
    )

    return hashlib.sha256(
        str(hashable_tuple).encode()
    ).hexdigest()
