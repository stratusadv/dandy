from abc import ABC, abstractmethod

from pydantic import BaseModel
from typing import Any, Union

import dandy.consts


class BaseCache(ABC, BaseModel):
    cache_name: str
    limit: int

    @abstractmethod
    def __len__(self) -> int:
        pass

    @abstractmethod
    def get(self, key: str) -> Union[Any, None]:
        pass

    @abstractmethod
    def set(self, key: str, value: Any):
        pass

    @abstractmethod
    def clean(self):
        pass

    @classmethod
    @abstractmethod
    def clear(cls, cache_name: str = dandy.consts.DEFAULT_CACHE_NAME):
        pass

    @classmethod
    @abstractmethod
    def clear_all(cls):
        pass

    @classmethod
    @abstractmethod
    def destroy_all(cls):
        pass
