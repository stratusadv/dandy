from abc import ABC
from pathlib import Path
from typing import Generic

from pydantic.main import IncEx
from typing_extensions import Type, Union, List

from dandy.agent import BaseAgent
from dandy.intel.type_vars import IntelType
from dandy.agent.strategy.strategy import BaseAgentStrategy
from dandy.llm.bot.llm_bot import BaseLlmBot
from dandy.llm.intel import DefaultLlmIntel
from dandy.llm.processor.llm_processor import BaseLlmProcessor
from dandy.llm.prompt.prompt import Prompt
from dandy.llm.service.config import LlmConfigOptions
from dandy.llm.service.request.message import MessageHistory


class BaseLlmAgent(BaseLlmBot, BaseAgent, ABC, Generic[IntelType]):
    config: str = 'DEFAULT'
    config_options: LlmConfigOptions = LlmConfigOptions()
    description: Union[Prompt, str, None] = None
    instructions_prompt: Prompt = Prompt("You're a helpful assistant please follow the users instructions.")
    intel_class: Type[IntelType] = DefaultLlmIntel
    strategy: Type[BaseAgentStrategy] | None = None

    @classmethod
    def process(
            cls,
            prompt: Union[Prompt, str],
            intel_class: Union[Type[IntelType], None] = None,
            intel_object: Union[IntelType, None] = None,
            images: Union[List[str], None] = None,
            image_files: Union[List[str | Path], None] = None,
            include_fields: Union[IncEx, None] = None,
            exclude_fields: Union[IncEx, None] = None,
            postfix_system_prompt: Union[Prompt, None] = None,
            message_history: Union[MessageHistory, None] = None,
    ) -> IntelType:

        return cls.process_prompt_to_intel(
            prompt=prompt,
            intel_class= intel_class or cls.intel_class,
            intel_object=intel_object,
            images=images,
            image_files=image_files,
            include_fields=include_fields,
            exclude_fields=exclude_fields,
            postfix_system_prompt=postfix_system_prompt,
            message_history=message_history,
        )
