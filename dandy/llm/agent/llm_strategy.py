from abc import ABC

from typing_extensions import Type, Sequence

from dandy.agent.resource import BaseAgentResource
from dandy.agent.strategy import BaseAgentStrategy
from dandy.core.processor.processor import BaseProcessor
from dandy.llm.agent.llm_resource import LlmAgentResource
from dandy.llm.bot.llm_bot import LlmBot


class BaseLlmAgentStrategy(BaseAgentStrategy, ABC):
    _resource_class: Type[BaseAgentResource] = LlmAgentResource
    resources: Sequence[Type[BaseProcessor]] = []


class DefaultLlmAgentStrategy(BaseLlmAgentStrategy):
    resources = (
        LlmBot,
    )