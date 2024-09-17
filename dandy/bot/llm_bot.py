from abc import ABC
from typing import Type

from dandy.bot.bot import Bot
from dandy.core.type_vars import ModelType
from dandy.llm.config import BaseLlmConfig
from dandy.llm.prompt import Prompt


class LlmBot(Bot, ABC):
    role_prompt: Prompt
    instructions_prompt: Prompt
    llm_config: BaseLlmConfig

    @classmethod
    def process_prompt_to_model_object(
            cls,
            prompt: Prompt,
            model: Type[ModelType],
    ) -> ModelType:

        return cls.llm_config.service.process_prompt_to_model_object(
            prompt=prompt,
            model=model,
            prefix_system_prompt=(
                Prompt()
                .prompt(cls.role_prompt)
                .prompt(cls.instructions_prompt)
            )
        )
