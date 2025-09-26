from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

import dandy.consts


class BaseCache(ABC, BaseModel):
    cache_name: str
    limit: int

    @abstractmethod
    def __len__(self) -> int:
        pass

    @abstractmethod
    def get(self, key: str) -> Any | None:
        pass

    @abstractmethod
    def set(self, key: str, value: Any):
        pass

    @abstractmethod
    def clean(self):
        pass

    @classmethod
    @abstractmethod
    def clear(cls, cache_name: str = dandy.consts.CACHE_DEFAULT_NAME):
        pass

    @classmethod
    @abstractmethod
    def clear_all(cls):
        pass

    @classmethod
    @abstractmethod
    def destroy_all(cls):
        pass
