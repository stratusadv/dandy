import hashlib


def generate_hash_key(*args, **kwargs) -> str:
    return hashlib.sha256(
        str(
            (args, tuple(sorted(kwargs.items())))
        ).encode()
    ).hexdigest()
