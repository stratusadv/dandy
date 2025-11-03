from typing import Any

from dandy.intel.intel import BaseIntel
from dandy.http.mixin import HttpServiceMixin
from dandy.intel.mixin import IntelServiceMixin
from dandy.llm.mixin import LlmServiceMixin
from dandy.llm.prompt.typing import PromptOrStr
from dandy.processor.bot.mixin import BotServiceMixin
from dandy.processor.processor import BaseProcessor
from dandy.vision.mixin import VisionServiceMixin


class Bot(
    BaseProcessor,
    BotServiceMixin,
    LlmServiceMixin,
    HttpServiceMixin,
    IntelServiceMixin,
    VisionServiceMixin,
):

    description: str | None = 'Generic Bot for performing generic tasks'

    def __init__(
            self,
            llm_randomize_seed: bool | None = None,
            llm_seed: int | None = None,
            llm_temperature: float | None = None,
            **kwargs
    ):
        super().__init__(
            **kwargs
        )

        self.llm_config_options.update_values(
            randomize_seed=llm_randomize_seed,
            seed=llm_seed,
            temperature=llm_temperature,
        )

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
