from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from dandy.llm.connector import LlmConnector


class BaseDiligence(ABC):
    trigger_level: float
    trigger_operator: Callable[[float, float], bool]

    def __init_subclass__(cls, **kwargs):
        if cls.trigger_level == 1.0 or cls.trigger_level > 2.0 or cls.trigger_level < 0.0:
            message = f'`{cls.__name__}` should have a trigger level between 0.0 and 2.0 and not 1.0 as it\'s used as the default.'
            raise ValueError(message)

    @classmethod
    def is_triggered(cls, level: float) -> bool:
        if cls.trigger_operator(level, cls.trigger_level):
            return True

        return False

    @classmethod
    @abstractmethod
    def apply(cls, llm_connector: LlmConnector) -> None:
        raise NotImplementedError
