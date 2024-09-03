from abc import abstractmethod, ABC
from typing import Any


class Handler(ABC):
    @classmethod
    @abstractmethod
    def process(cls, **kwargs: Any) -> Any:
        ...