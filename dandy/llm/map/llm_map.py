from abc import ABC
from pathlib import Path

from pydantic.main import IncEx
from typing_extensions import Type, Generic, Union, List

from dandy.core.future import AsyncFuture
from dandy.core.utils import encode_file_to_base64
from dandy.intel import BaseIntel
from dandy.intel.type_vars import IntelType
from dandy.llm.conf import llm_configs
from dandy.llm.intel import DefaultLlmIntel
from dandy.llm.processor.llm_processor import BaseLlmProcessor
from dandy.llm.prompt import Prompt
from dandy.llm.service.config.options import LlmConfigOptions


class BaseLlmMap(BaseLlmProcessor, ABC, Generic[IntelType]):
    config: str = 'DEFAULT'
    config_options: LlmConfigOptions = LlmConfigOptions()
    instructions_prompt: Prompt = Prompt("You're a helpful assistant please follow the users instructions.")
    intel_class: Type[BaseIntel] = DefaultLlmIntel

    @classmethod
    def process(
            cls,
            prompt: Union[Prompt, str],
            intel_class: Union[Type[IntelType], None] = None,
    ) -> IntelType:
        raise NotImplementedError

    @classmethod
    def process_prompt_to_intel(
            cls,
            prompt: Union[Prompt, str],
            intel_class: Union[Type[IntelType], None] = None,
    ) -> IntelType:

        system_prompt = Prompt()
        system_prompt.prompt(cls.instructions_prompt)

        return llm_configs[cls.config].generate_service(
            llm_options=cls.config_options
        ).process_prompt_to_intel(
            prompt=prompt if isinstance(prompt, Prompt) else Prompt(prompt),
            intel_class=intel_class,
            system_prompt=system_prompt
        )

    @classmethod
    def process_to_future(cls, *args, **kwargs) -> AsyncFuture[IntelType]:
        return AsyncFuture[IntelType](cls.process, *args, **kwargs)


