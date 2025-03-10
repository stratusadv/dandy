import hashlib


def generate_hash_key(qualname: str, *args, **kwargs) -> str:
    return hashlib.sha256(
        str(
            (qualname, args, tuple(sorted(kwargs.items())))
        ).encode()
    ).hexdigest()
