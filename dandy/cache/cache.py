from abc import ABC, abstractmethod

from pydantic import BaseModel
from typing_extensions import Any, Union


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
    
    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def destroy(self):
        pass

