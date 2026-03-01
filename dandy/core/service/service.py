from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from dandy.recorder.utils import generate_recorder_event_id

T_co = TypeVar('T_co', bound=Any, covariant=True)


class BaseService(ABC, Generic[T_co]):
    def __init__(self, obj: T_co) -> None:
        self.recorder_event_id = generate_recorder_event_id()
        self.obj = obj

        self.__post_init__()

    def __post_init__(self) -> None:
        pass

    @property
    def obj_class(self) -> type[T_co]:
        return self.obj.__class__

    @abstractmethod
    def reset(self) -> None:
        raise NotImplementedError
