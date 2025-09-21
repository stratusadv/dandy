from abc import ABC, abstractmethod

from typing import Type, Any

from dandy.processor.agent.exceptions import AgentCriticalException
from dandy.processor.processor import BaseProcessor


class BaseProcessorController(ABC):
    def __init__(
            self,
            processor: Type[BaseProcessor]
    ):
        if not issubclass(processor, BaseProcessor):
            message = f'{processor} is not a sub class of "BaseProcessor"'
            raise AgentCriticalException(message)

        self.processor = processor

    @abstractmethod
    def use(self, *args, **kwargs) -> Any:
        raise NotImplementedError
