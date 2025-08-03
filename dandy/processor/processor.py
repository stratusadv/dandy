from abc import abstractmethod, ABC

from typing import Any, Union

from dandy.core.future import AsyncFuture
from dandy.processor.abc_meta import ProcessorABCMeta


class BaseProcessor(ABC, metaclass=ProcessorABCMeta):
    _recorder_event_id: str = ''
    description: Union[str, None] = None

    @abstractmethod
    def process(self, *args, **kwargs) -> Any:
        raise NotImplementedError

    def process_to_future(self, *args, **kwargs) -> AsyncFuture:
        return AsyncFuture(self.process, *args, **kwargs)