from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from dandy.bot.service import BotService
from dandy.core.processor.processor import BaseProcessor
from dandy.http.mixin import HttpProcessorMixin
from dandy.llm.mixin import LlmProcessorMixin
from dandy.vision.mixin import VisionProcessorMixin


@dataclass(kw_only=True)
class Bot(
    BaseProcessor,
    LlmProcessorMixin,
    HttpProcessorMixin,
    VisionProcessorMixin,
    ABC,
):
    services: BotService = BotService()
    description = 'Base Dandy Bot Class That Can Do Anything'

    def process(self, *args, **kwargs) -> Any:
        pass
