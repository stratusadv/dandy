from abc import ABC

from typing_extensions import Type, Generic

from dandy.bot import Bot
from dandy.bot.exceptions import BotException
from dandy.future.future import AsyncFuture
from dandy.intel import BaseIntel
from dandy.intel.type_vars import IntelType
from dandy.llm.conf import llm_configs
from dandy.llm.intel import DefaultLlmIntel
from dandy.llm.prompt import Prompt
from dandy.llm.service.config.options import LlmConfigOptions


class BaseLlmBot(Bot, ABC, Generic[IntelType]):
    config: str = 'DEFAULT'
    config_options: LlmConfigOptions = LlmConfigOptions()
    instructions_prompt: Prompt
    intel_class: Type[BaseIntel] = DefaultLlmIntel

    def __new__(cls):
        if cls.config is None:
            raise BotException(f'{cls.__name__} config is not set')
        if cls.instructions_prompt is None:
            raise BotException(f'{cls.__name__} instructions_prompt is not set')

        return super().__new__(cls)

    @classmethod
    def process_prompt_to_intel(
            cls,
            prompt: Prompt,
            intel_class: Type[IntelType],
    ) -> IntelType:

        return llm_configs[cls.config].generate_service(
            llm_options=cls.config_options
        ).process_prompt_to_intel(
            prompt=prompt,
            intel_class=intel_class,
            prefix_system_prompt=(
                Prompt()
                .prompt(cls.instructions_prompt)
            )
        )

    @classmethod
    def process_to_future(cls, *args, **kwargs) -> AsyncFuture[IntelType]:
        return AsyncFuture[IntelType](cls.process, *args, **kwargs)


class LlmBot(BaseLlmBot, Generic[IntelType]):
    instructions_prompt: Prompt = Prompt("You're a helpful assistant.")

    @classmethod
    def process(
            cls,
            prompt: Prompt,
            intel_class: Type[IntelType] = DefaultLlmIntel,
    ) -> IntelType:

        return cls.process_prompt_to_intel(
            prompt,
            intel_class or cls.intel_class
        )

