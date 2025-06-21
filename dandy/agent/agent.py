from abc import ABC, ABCMeta

from typing_extensions import Type, Sequence

from dandy.agent.exceptions import AgentCriticalException
from dandy.core.processor.processor import BaseProcessor
from dandy.conf import settings
from dandy.core.processor.strategy import BaseProcessorsStrategy


class BaseAgent(BaseProcessor, ABC):
    plan_time_limit_seconds: int = settings.DEFAULT_AGENT_PLAN_TIME_LIMIT_SECONDS
    plan_task_count_limit: int = settings.DEFAULT_AGENT_PLAN_TASK_COUNT_LIMIT
    _processors_strategy_class: Type[BaseProcessorsStrategy]
    _processors_strategy: BaseProcessorsStrategy
    processors: Sequence[Type[BaseProcessor]]

    def __init_subclass__(cls, **kwargs):
        if cls.processors is None or len(cls.processors) == 0:
            raise AgentCriticalException(
                f'{cls.__name__} must have a sequence of "BaseProcessor" sub classes defined on the "processors" class attribute.'
            )

        if cls._processors_strategy_class is None:
            raise AgentCriticalException(
                f'{cls.__name__} must have a "BaseProcessorsStrategy" sub class defined on the "_processors_strategy_class" class attribute.'
            )

        else:
            cls._processors_strategy = cls._processors_strategy_class(
                cls.processors
            )