from dataclasses import dataclass
from typing import ClassVar

from dandy.http.mixin import HttpServiceMixin
from dandy.intel.mixin import IntelServiceMixin
from dandy.intel.typing import IntelType
from dandy.llm.mixin import LlmServiceMixin
from dandy.llm.prompt.typing import PromptOrStr
from dandy.processor.bot.service import BotService
from dandy.processor.processor import BaseProcessor
from dandy.vision.mixin import VisionProcessorMixin


@dataclass(kw_only=True)
class Bot(
    BaseProcessor,
    LlmServiceMixin,
    HttpServiceMixin,
    IntelServiceMixin,
    VisionProcessorMixin,
):
    services: ClassVar[BotService] = BotService()
    _BotService_instance: BotService | None = None

    description = 'Base Dandy Bot Class That Can Do Anything'

    def process(
            self,
            prompt: PromptOrStr,
            intel_class: type[IntelType] | None = None,
    ) -> IntelType:
        return self.llm.prompt_to_intel(
            prompt=prompt,
            intel_class=intel_class,
        )
