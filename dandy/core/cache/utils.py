import hashlib


def generate_hash_key(func: object, *args, **kwargs) -> str:
    hashable_tuple = (
        func.__module__,
        func.__qualname__,
        args,
        tuple(sorted(kwargs.items()))
    )

    print(f'Hashable Tuple: {hashable_tuple}')

    hash_key = hashlib.sha256(
        str(hashable_tuple).encode()
    ).hexdigest()

    print(f'Hash Key: {hash_key}')

    return hash_key
