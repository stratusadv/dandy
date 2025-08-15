from dandy.llm.conf import llm_configs
from dandy.llm.prompt.typing import PromptOrStr, PromptOrStrOrNone
from dandy.llm.config import LlmConfigOptions
from dandy.llm.service.service import LlmService


class LlmProcessorMixin:
    llm_config: str = 'DEFAULT'
    llm_config_options: LlmConfigOptions = llm_configs['DEFAULT'].options
    llm_instructions_prompt: PromptOrStr = 'You are a helpful assistant.'
    llm_system_override_prompt: PromptOrStrOrNone = None

    llm: LlmService = LlmService()
