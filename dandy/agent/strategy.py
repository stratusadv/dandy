from __future__ import annotations

from abc import ABC

from typing_extensions import Type, Sequence, TYPE_CHECKING, List

from dandy.agent.exceptions import AgentCriticalException
from dandy.agent.resource import BaseAgentResource
from dandy.bot import BaseBot
from dandy.core.processor.processor import BaseProcessor
from dandy.intel import BaseIntel
from dandy.workflow import BaseWorkflow

if TYPE_CHECKING:
    from dandy.llm.agent.llm_agent import BaseAgent


class BaseAgentStrategy(ABC):
    _resources_names: List[str] = [
        'agents',
        'bots',
        'workflows',
    ]

    _resource_class: Type[BaseAgentResource]

    agents: Sequence[Type[BaseAgent]] | None = None
    bots: Sequence[Type[BaseBot]] | None = None
    workflows: Sequence[Type[BaseWorkflow]] | None = None

    def __init_subclass__(cls):
        super().__init_subclass__()

        if cls._resource_class is None:
            raise AgentCriticalException(f'{cls.__name__}._resource_class is not set')

        for resources_name in cls._resources_names:
            resources = cls._get_resources(resources_name)

            if resources:
                for resource_type in resources:
                    if not issubclass(resource_type, BaseProcessor):
                        raise AgentCriticalException(
                            f'All agents, bots and workflows must be sub classed from "BaseProcessor" sub class.'
                        )

                    if resource_type.description is None:
                        raise AgentCriticalException(
                            f'{resource_type.__name__} did not have the class attribute "description". All resources used in an "AgentStrategy" must have a description.'
                        )

    @classmethod
    def as_dict(cls) -> dict:
        strategy_resources_dict = {}

        for resources_name in cls._resources_names:
            resources = cls._get_resources(resources_name)

            if resources is not None and len(resources) > 0:
                for index, resource in enumerate(resources):
                    strategy_resources_dict[
                        cls._resources_to_key(index, resources_name)
                    ] = resource.description

        return strategy_resources_dict

    @classmethod
    def get_resource_from_key(cls, key: str) -> BaseAgentResource:
        resources_name = '_'.join(key.split('_')[0:-1])
        index = int(key.split('_')[-1])

        resources = cls._get_resources(resources_name)

        return cls._resource_class(resources[index])

    @classmethod
    def _get_resources(cls, resources_name: str) -> Sequence[Type[BaseProcessor]]:
        return getattr(cls, resources_name)

    @classmethod
    def get_resource_processor_module_and_qualname_from_key(cls, key: str) -> str:
        processor = cls.get_resource_from_key(key).processor
        return f'{processor.__module__}.{processor.__qualname__}'

    @classmethod
    def _resources_to_key(cls, index: int, resources_name: str, ) -> str:
        return f'{resources_name}_{index}'
