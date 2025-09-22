from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import Any

from dandy.core.future import AsyncFuture
from dandy.processor.recorder import record_process_wrapper


@dataclass(kw_only=True)
class BaseProcessor(
    ABC,
):
    _recorder_event_id: str = ''
    description: str | None = None

    def __init_subclass__(cls):
        super().__init_subclass__()

        if ABC not in cls.__bases__:
            # Typing Does not work properly for processors if you override __getattribute__ in the BaseProcessor class.
            # This is a workaround and should be fixed in future versions of the python lsp.
            def __getattribute__(self, name):
                attr = super().__getattribute__(name)

                if name == 'process' and callable(attr) and not hasattr(attr, '_wrapped'):
                    wrapped = record_process_wrapper(self, attr)
                    wrapped._wrapped = True
                    return wrapped

                return attr

            setattr(cls, '__getattribute__', __getattribute__)

    def process(self, *args, **kwargs) -> Any:
        raise NotImplementedError

    def process_to_future(self, *args, **kwargs) -> AsyncFuture:
        return AsyncFuture(self.process, *args, **kwargs)
