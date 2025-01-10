from abc import ABC
from typing_extensions import Type, Union

from dandy.bot.bot import Bot
from dandy.bot.exceptions import BotException
from dandy.core.type_vars import ModelType
from dandy.llm.config import BaseLlmConfig
from dandy.llm.config.options import LlmConfigOptions
from dandy.llm.prompt import Prompt
from dandy.llm.conf import llm_configs


class LlmBot(Bot, ABC):
    instructions_prompt: Prompt
    config: BaseLlmConfig = llm_configs.DEFAULT

    max_input_tokens: Union[int, None] = None
    max_output_tokens: Union[int, None] = None
    randomize_seed: Union[bool, None] = None
    seed: Union[int, None] = None
    temperature: Union[float, None] = None

    def __new__(cls, *args, **kwargs):
        if cls.config is None:
            raise BotException(f'{cls.__name__} config is not set')
        if cls.instructions_prompt is None:
            raise BotException(f'{cls.__name__} instructions_prompt is not set')

        return super().__new__(cls)

    @classmethod
    def process_prompt_to_model_object(
            cls,
            prompt: Prompt,
            model: Type[ModelType],
    ) -> ModelType:

        return cls.config.generate_service(
            llm_options=LlmConfigOptions(
                seed=cls.seed,
                randomize_seed=cls.randomize_seed,
                temperature=cls.temperature,
                max_input_tokens=cls.max_input_tokens,
                max_output_tokens=cls.max_output_tokens
            )
        ).process_prompt_to_model_object(
            prompt=prompt,
            model=model,
            prefix_system_prompt=(
                Prompt()
                .prompt(cls.instructions_prompt)
            )
        )
