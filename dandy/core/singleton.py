from typing import Any


class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs) -> Any:
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
