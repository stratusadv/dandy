from dataclasses import dataclass

from dandy.llm.conf import llm_configs
from dandy.llm.exceptions import LlmCriticalException
from dandy.llm.prompt.typing import PromptOrStr, PromptOrStrOrNone
from dandy.llm.config import LlmConfigOptions
from dandy.llm.service.service import LlmService


@dataclass
class LlmProcessorMixin:
    llm_config: str = 'DEFAULT'
    llm_config_options: LlmConfigOptions = llm_configs['DEFAULT'].options
    llm_instructions_prompt: PromptOrStr = 'You are a helpful assistant.'
    llm_system_override_prompt: PromptOrStrOrNone = None

    llm: LlmService = LlmService()

    def __init_subclass__(cls):
        super().__init_subclass__()
        for attr in [
            'llm_config',
            'llm_config_options',
            'llm_instructions_prompt'
        ]:
            if getattr(cls, attr) is None:
                raise LlmCriticalException(f'{cls.__name__} {attr} is not set')
