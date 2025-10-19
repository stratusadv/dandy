from typing import ClassVar, Any

from dandy.intel.intel import BaseIntel
from dandy.http.mixin import HttpServiceMixin
from dandy.intel.mixin import IntelServiceMixin
from dandy.llm.mixin import LlmServiceMixin
from dandy.llm.prompt.typing import PromptOrStr
from dandy.processor.bot.service import BotService
from dandy.processor.processor import BaseProcessor
from dandy.vision.mixin import VisionProcessorMixin


class Bot(
    BaseProcessor,
    LlmServiceMixin,
    HttpServiceMixin,
    IntelServiceMixin,
    VisionProcessorMixin,
):
    services: ClassVar[BotService] = BotService()
    _BotService_instance: BotService | None = None

    description: str | None = 'Generic Bot for performing generic tasks'

    @classmethod
    def get_description(cls) -> str | None:
        if cls.description is not None:
            return cls.description

        return cls.get_llm_description()

    def process(
            self,
            *args,
            **kwargs,
    ) -> Any:
        if len(args) >= 1 and isinstance(args[0], PromptOrStr):
            kwargs['prompt'] = args[0]

        if len(args) == 2 and issubclass(args[1], BaseIntel):
            kwargs['intel_class'] = args[1]

        if 'prompt' in kwargs:
            return self.llm.prompt_to_intel(
                **kwargs
            )

        message = '`Bot.process` requires key word argument `prompt`.'
        raise ValueError(message)
