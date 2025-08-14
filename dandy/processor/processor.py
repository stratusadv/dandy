from abc import abstractmethod, ABC

from typing import Any, Union, get_type_hints

from dandy.core.future import AsyncFuture
from dandy.processor.abc_meta import ProcessorABCMeta


class BaseProcessor(ABC, metaclass=ProcessorABCMeta):
    _recorder_event_id: str = ''
    description: Union[str, None] = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._field_types = get_type_hints(cls)

    def __init__(self, **kwargs):
        for field_name, value in kwargs.items():
            if field_name in self._field_types:
                expected_type = self._field_types[field_name]
                if not isinstance(value, expected_type):
                    raise TypeError(f"{field_name} must be {expected_type}")
            setattr(self, field_name, value)

        self.__post_init__()

    def __post_init__(self):
        ...

    @abstractmethod
    def process(self, *args, **kwargs) -> Any:
        raise NotImplementedError

    def process_to_future(self, *args, **kwargs) -> AsyncFuture:
        return AsyncFuture(self.process, *args, **kwargs)