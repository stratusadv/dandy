from __future__ import annotations

from abc import ABC

from typing_extensions import Type, Iterable, TYPE_CHECKING, List

from dandy.agent.exceptions import AgentCriticalException
from dandy.bot import BaseBot
from dandy.core.processor.processor import BaseProcessor
from dandy.workflow import BaseWorkflow

if TYPE_CHECKING:
    from dandy.llm.agent.llm_agent import BaseAgent


class BaseAgentStrategy(ABC):
    _resources: List[str] = [
        'agents',
        'bots',
        'workflows',
    ]

    agents: Iterable[Type[BaseAgent]] | None = None
    bots: Iterable[Type[BaseBot]] | None = None
    workflows: Iterable[Type[BaseWorkflow]] | None = None

    def __init_subclass__(cls):
        super().__init_subclass__()

        for resources in cls._resources:
            resource = getattr(cls, resources)

            if resource:
                for resource_type in resource:
                    if not issubclass(resource_type, BaseProcessor):
                        raise AgentCriticalException(f'All agents, bots and workflows must be sub classed from "BaseProcessor" sub class.')

                    if resource_type.description is None:
                        raise AgentCriticalException(f'{resource_type.__name__} did not have the class attribute "description". All agents, bots and workflows used in an "AgentStrategy" must have a description.')




