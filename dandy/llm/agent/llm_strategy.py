from abc import ABC

from typing_extensions import List, Iterable, Type

from dandy.agent.resource import BaseAgentResource
from dandy.agent.strategy import BaseAgentStrategy
from dandy.llm.agent.llm_resource import LlmAgentResource
from dandy.llm.bot.llm_bot import LlmBot
from dandy.llm.map.llm_map import BaseLlmMap


class BaseLlmAgentStrategy(BaseAgentStrategy, ABC):
    _resources_names: List[str] = [
        'agents',
        'bots',
        'workflows',
        'maps',
    ]
    _resource_class: Type[BaseAgentResource] = LlmAgentResource

    maps: Iterable[Type[BaseLlmMap]] | None = None

    def __init_subclass__(cls):
        super().__init_subclass__()


class DefaultLlmAgentStrategy(BaseLlmAgentStrategy):
    bots = (
        LlmBot,
    )