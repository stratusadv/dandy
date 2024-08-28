from abc import ABCMeta, abstractmethod
from typing import Any



class Bot(metaclass=ABCMeta):
    @abstractmethod
    def process(self, **kwargs: Any) -> Any:
        pass