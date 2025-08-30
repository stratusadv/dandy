from dataclasses import dataclass
from typing import Any, ClassVar

from dandy.http.mixin import HttpProcessorMixin
from dandy.llm.mixin import LlmProcessorMixin
from dandy.processor.bot.service import BotService
from dandy.processor.processor import BaseProcessor
from dandy.vision.mixin import VisionProcessorMixin


@dataclass(kw_only=True)
class Bot(
    BaseProcessor,
    LlmProcessorMixin,
    HttpProcessorMixin,
    VisionProcessorMixin,
):
    services: ClassVar[BotService] = BotService()
    description = 'Base Dandy Bot Class That Can Do Anything'

    def process(self, *args, **kwargs) -> Any:
        pass
