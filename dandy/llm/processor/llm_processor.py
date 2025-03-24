from abc import ABC, abstractmethod

from typing_extensions import Type, Generic

from dandy.core.exceptions import DandyCriticalException
from dandy.core.future import AsyncFuture
from dandy.core.processor.processor import BaseProcessor
from dandy.intel import BaseIntel
from dandy.intel.type_vars import IntelType
from dandy.llm.prompt import Prompt
from dandy.llm.service.config.options import LlmConfigOptions


class BaseLlmProcessor(BaseProcessor, ABC, Generic[IntelType]):
    config: str
    config_options: LlmConfigOptions
    instructions_prompt: Prompt
    intel_class: Type[BaseIntel]

    def __init_subclass__(cls):
        super().__init_subclass__()
        for attr in ['config', 'config_options', 'instructions_prompt', 'intel_class']:
            if getattr(cls, attr) is None:
                raise DandyCriticalException(f'{cls.__name__} {attr} is not set')


    @classmethod
    @abstractmethod
    def process_prompt_to_intel(
            cls,
            *args,
            **kwargs,
    ) -> IntelType:
        raise NotImplementedError

    @classmethod
    def process_to_future(cls, *args, **kwargs) -> AsyncFuture[IntelType]:
        return AsyncFuture[IntelType](cls.process, *args, **kwargs)
