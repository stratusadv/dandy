from abc import ABC

from typing_extensions import Type

from dandy.core.processor.controller import BaseProcessorController
from dandy.core.processor.strategy import BaseProcessorsStrategy
from dandy.llm.processor.llm_controller import LlmProcessorController


class BaseLlmProcessorsStrategy(BaseProcessorsStrategy, ABC):
    _processor_controller: Type[BaseProcessorController] = LlmProcessorController
