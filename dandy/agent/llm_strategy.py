from abc import ABC

from typing import Type

from dandy.agent.llm_controller import LlmProcessorController
from dandy.core.processor.controller import BaseProcessorController
from dandy.core.processor.strategy import BaseProcessorsStrategy


class BaseLlmProcessorsStrategy(BaseProcessorsStrategy, ABC):
    _processor_controller: Type[BaseProcessorController] = LlmProcessorController
