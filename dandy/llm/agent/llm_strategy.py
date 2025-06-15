from abc import ABC
from typing import Union

from typing_extensions import List, Iterable, Type

from dandy.agent.strategy.strategy import BaseAgentStrategy
from dandy.bot.bot import BaseBot
from dandy.llm.map.llm_map import BaseLlmMap
from dandy.llm.bot.llm_bot import Prompt, LlmBot



class BaseLlmAgentStrategy(BaseAgentStrategy, ABC):
    _resources_names: List[str] = [
        'agents',
        'bots',
        'workflows',
        'maps',
    ]

    maps: Iterable[Type[BaseLlmMap]] | None = None

    def __init_subclass__(cls):
        super().__init_subclass__()


class DefaultLlmAgentStrategy(BaseLlmAgentStrategy):
    bots = (
        LlmBot,
    )