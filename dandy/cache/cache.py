from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from dandy.constants import CACHE_DEFAULT_NAME


class BaseCache(ABC, BaseModel):
    cache_name: str
    limit: int

    @abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def get(self, key: str) -> Any | None:
        raise NotImplementedError

    @abstractmethod
    def set(self, key: str, value: Any):
        raise NotImplementedError

    @abstractmethod
    def clean(self):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def clear(cls, cache_name: str = CACHE_DEFAULT_NAME):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def clear_all(cls):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def destroy_all(cls):
        raise NotImplementedError
