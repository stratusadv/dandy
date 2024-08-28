from abc import ABCMeta
from typing import Type

from dandy.bot.bot import Bot
from dandy.core.type_vars import ModelType
from dandy.llm.prompt import Prompt


class LlmBot(Bot, metaclass=ABCMeta):
    role_prompt: Prompt
    instructions_prompt: Prompt

    @classmethod
    def process_prompt_to_model_object(
            cls,
            prompt: Prompt,
            model: Type[ModelType],
    ) -> ModelType:

        from dandy import config

        return config.active_llm_service.process_prompt_to_model_object(
            prompt=prompt,
            model=model,
            prefix_system_prompt=(
                Prompt()
                .prompt(cls.role_prompt)
                .prompt(cls.instructions_prompt)
            )
        )
