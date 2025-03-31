from typing_extensions import Type

from dandy.agent.agent import BaseAgent
from dandy.intel import BaseIntel
from dandy.intel.type_vars import IntelType
from dandy.llm import LlmConfigOptions, Prompt
from dandy.llm.processor.llm_processor import BaseLlmProcessor


class BaseLlmAgent(BaseLlmProcessor, BaseAgent):
    config: str
    config_options: LlmConfigOptions
    instructions_prompt: Prompt
    intel_class: Type[BaseIntel]

    @classmethod
    def process(
            cls,
            *args,
            **kwargs
    ) -> IntelType:
        pass


    @classmethod
    def process_prompt_to_intel(
            cls,
            *args,
            **kwargs,
    ) -> IntelType:
        pass


class LlmAgent(BaseLlmAgent):
    pass