from abc import ABC, abstractmethod

from typing_extensions import Type

from dandy.agent.exceptions import AgentCriticalException
from dandy.core.processor.processor import BaseProcessor
from dandy.intel import BaseIntel


class BaseAgentResource(ABC):
    def __init__(
            self,
            processor: Type[BaseProcessor]
    ):
        if not issubclass(processor, BaseProcessor):
            raise AgentCriticalException(f'{processor} is not a sub class of "BaseProcessor"')

        self.processor = processor

    @abstractmethod
    def use(self, *args, **kwargs) -> BaseIntel | None:
        raise NotImplementedError
