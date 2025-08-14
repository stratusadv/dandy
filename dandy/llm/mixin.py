from dandy.llm.conf import llm_configs
from dandy.llm.prompt import Prompt
from dandy.llm.service.config import LlmConfigOptions, BaseLlmConfig
from dandy.llm.service.llm_service import LlmService


class LlmProcessorMixin:
    llm_config: BaseLlmConfig = llm_configs.DEFAULT
    llm_config_options: LlmConfigOptions = llm_configs.DEFAULT.options
    llm_instructions_prompt: Prompt = 'You are a helpful assistant.'
    llm: LlmService = LlmService()
