from dataclasses import dataclass
from typing import ClassVar

from dandy import BaseIntel
from dandy.http.mixin import HttpProcessorMixin
from dandy.intel.typing import IntelType
from dandy.llm.mixin import LlmProcessorMixin
from dandy.llm.prompt.typing import PromptOrStr
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

    def process(
            self,
            prompt: PromptOrStr,
            intel_class: type[IntelType] | None = None,
    ) -> IntelType:
        return self.llm.prompt_to_intel(
            prompt=prompt,
            intel_class=intel_class,
        )
