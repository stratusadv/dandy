from abc import abstractmethod, ABC
from dataclasses import dataclass

from typing import Any, get_type_hints

from dandy.core.future import AsyncFuture
from dandy.core.processor.abc_meta import ProcessorABCMeta


@dataclass(kw_only=True)
class BaseProcessor(
    ABC,
    metaclass=ProcessorABCMeta
):
    _recorder_event_id: str = ''
    description: str | None = None

    @abstractmethod
    def process(self, *args, **kwargs) -> Any:
        raise NotImplementedError

    def process_to_future(self, *args, **kwargs) -> AsyncFuture:
        return AsyncFuture(self.process, *args, **kwargs)