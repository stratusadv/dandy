from abc import abstractmethod

from typing_extensions import Any

from dandy.future.future import AsyncFuture
from dandy.processor.abc_meta import ProcessorABCMeta


class BaseProcessor(metaclass=ProcessorABCMeta):
    @classmethod
    @abstractmethod
    def process(cls, *args, **kwargs) -> Any:
        ...

    @classmethod
    def process_to_future(cls, *args, **kwargs) -> AsyncFuture:
        return AsyncFuture(cls.process, *args, **kwargs)
