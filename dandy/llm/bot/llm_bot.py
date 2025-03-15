from abc import ABC
from pathlib import Path

from pydantic.main import IncEx
from typing_extensions import Type, Generic, Union, List

from dandy.bot.bot import BaseBot
from dandy.bot.exceptions import BotCriticalException
from dandy.core.future import AsyncFuture
from dandy.core.utils import encode_file_to_base64
from dandy.intel import BaseIntel
from dandy.intel.type_vars import IntelType
from dandy.llm.conf import llm_configs
from dandy.llm.intel import DefaultLlmIntel
from dandy.llm.prompt import Prompt
from dandy.llm.service.config.options import LlmConfigOptions


class BaseLlmBot(BaseBot, ABC, Generic[IntelType]):
    config: str = 'DEFAULT'
    config_options: LlmConfigOptions = LlmConfigOptions()
    instructions_prompt: Prompt = Prompt("You're a helpful assistant please follow the users instructions.")
    intel_class: Type[BaseIntel] = DefaultLlmIntel

    def __new__(cls):
        if cls.config is None:
            raise BotCriticalException(f'{cls.__name__} config is not set')
        if cls.instructions_prompt is None:
            raise BotCriticalException(f'{cls.__name__} instructions_prompt is not set')

        return super().__new__(cls)

    @classmethod
    def process_prompt_to_intel(
            cls,
            prompt: Union[Prompt, str],
            intel_class: Union[Type[IntelType], None] = None,
            intel_object: Union[IntelType, None] = None,
            images: Union[List[str], None] = None,
            image_files: Union[List[str | Path], None] = None,
            include_fields: Union[IncEx, None] = None,
            exclude_fields: Union[IncEx, None] = None,
            postfix_system_prompt: Union[Prompt, None] = None
    ) -> IntelType:

        if image_files:
            images = [] if images is None else images

            for image_file in image_files:
                images.append(encode_file_to_base64(image_file))

        system_prompt = Prompt()
        system_prompt.prompt(cls.instructions_prompt)
        
        if postfix_system_prompt:
            system_prompt.line_break()
            system_prompt.prompt(postfix_system_prompt)

        return llm_configs[cls.config].generate_service(
            llm_options=cls.config_options
        ).process_prompt_to_intel(
            prompt=prompt if isinstance(prompt, Prompt) else Prompt(prompt),
            intel_class=intel_class,
            intel_object=intel_object,
            images=images,
            include_fields=include_fields,
            exclude_fields=exclude_fields,
            system_prompt=system_prompt
        )

    @classmethod
    def process_to_future(cls, *args, **kwargs) -> AsyncFuture[IntelType]:
        return AsyncFuture[IntelType](cls.process, *args, **kwargs)


class LlmBot(BaseLlmBot, Generic[IntelType]):
    @classmethod
    def process(
            cls,
            prompt: Union[Prompt, str],
            intel_class: Type[IntelType] = DefaultLlmIntel,
    ) -> IntelType:

        return cls.process_prompt_to_intel(
            prompt,
            intel_class or cls.intel_class
        )

