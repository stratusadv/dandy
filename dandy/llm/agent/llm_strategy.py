from typing_extensions import List, Iterable, Type

from dandy.agent.strategy.strategy import BaseAgentStrategy
from dandy.llm import BaseLlmMap


class BaseLlmAgentStrategy(BaseAgentStrategy):
    _resources: List[str] = [
        'agents',
        'bots',
        'workflows',
        'maps',
    ]

    maps: Iterable[Type[BaseLlmMap]] | None = None

    def __init_subclass__(cls):
        super().__init_subclass__()

