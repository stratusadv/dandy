from abc import ABC
from typing_extensions import Type, Union

from dandy.bot.bot import Bot
from dandy.core.type_vars import ModelType
from dandy.llm.config import BaseLlmConfig
from dandy.llm.prompt import Prompt


class LlmBot(Bot, ABC):
    instructions_prompt: Prompt
    llm_config: BaseLlmConfig
    llm_temperature: Union[float, None] = None
    llm_seed: Union[int, None] = None
    llm_max_input_tokens: Union[int, None] = None
    llm_max_output_tokens: Union[int, None] = None

    @classmethod
    def process_prompt_to_model_object(
            cls,
            prompt: Prompt,
            model: Type[ModelType],
    ) -> ModelType:

        return cls.llm_config.generate_service(
            seed=cls.llm_seed,
            temperature=cls.llm_temperature,
            max_input_tokens=cls.llm_max_input_tokens,
            max_output_tokens=cls.llm_max_output_tokens
        ).process_prompt_to_model_object(
            prompt=prompt,
            model=model,
            prefix_system_prompt=(
                Prompt()
                .prompt(cls.instructions_prompt)
            )
        )
