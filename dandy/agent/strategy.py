from __future__ import annotations

from abc import ABC

from typing_extensions import Type, Sequence, TYPE_CHECKING

from dandy.agent.exceptions import AgentCriticalException
from dandy.agent.resource import BaseAgentResource
from dandy.core.processor.processor import BaseProcessor

if TYPE_CHECKING:
    pass


class BaseAgentStrategy(ABC):
    _resource_class: Type[BaseAgentResource]
    resources: Sequence[Type[BaseProcessor]]

    def __init_subclass__(cls):
        super().__init_subclass__()

        if cls._resource_class is None:
            raise AgentCriticalException(f'{cls.__name__}._resource_class is not set')

        if cls.resources is None:
            raise AgentCriticalException(f'{cls.__name__}.resources is not set')

        for resource in cls.resources:
            if not issubclass(resource, BaseProcessor):
                raise AgentCriticalException(
                    'All resources must be sub classed from the "BaseProcessor" sub class.'
                )

            if resource.description is None:
                raise AgentCriticalException(
                    f'{resource.__name__} did not have the class attribute "description". All "BaseProcessor" resources used in an "AgentStrategy" must have a "description" class attribute.'
                )

    @classmethod
    def as_dict(cls) -> dict:
        strategy_resources_dict = {}

        for index, resource in enumerate(cls.resources):
            strategy_resources_dict[index] = resource.description

        return strategy_resources_dict

    @classmethod
    def get_resource_from_key(cls, key: int) -> BaseAgentResource:
        return cls._resource_class(cls.resources[int(key)])

    @classmethod
    def _get_resources(cls, resources_name: str) -> Sequence[Type[BaseProcessor]]:
        return getattr(cls, resources_name)

    @classmethod
    def get_resource_processor_module_and_qualname_from_key(cls, key: int) -> str:
        processor = cls.get_resource_from_key(key).processor
        return f'{processor.__module__}.{processor.__qualname__}'
