from typing_extensions import Union, Self

from pydantic import BaseModel, Field

from dandy.conf import settings
from dandy.llm.config.utils import generate_random_seed


class LlmConfigOptions:
    def __init__(
            self,
            seed: Union[int, None] = None,
            randomize_seed: Union[bool, None] = None,
            max_input_tokens: Union[int, None] = None,
            max_output_tokens: Union[int, None] = None,
            temperature: Union[float, None] = None,
            connection_retry_count: Union[int, None] = None,
            prompt_retry_count: Union[int, None] = None,
    ):
        self._seed = seed
        self._randomize_seed = randomize_seed
        self._max_input_tokens = max_input_tokens
        self._max_output_tokens = max_output_tokens
        self._temperature = temperature
        self._connection_retry_count = connection_retry_count
        self._prompt_retry_count = prompt_retry_count

    @property
    def seed(self) -> Union[int, None]:
        if self._randomize_seed:
            return generate_random_seed()

        return self._seed if self._seed is not None else settings.DEFAULT_LLM_SEED

    @property
    def max_input_tokens(self) -> Union[int, None]:
        return self._max_input_tokens if self._max_input_tokens is not None else settings.DEFAULT_LLM_MAX_INPUT_TOKENS

    @property
    def max_output_tokens(self) -> Union[int, None]:
        return self._max_output_tokens if self._max_output_tokens is not None else settings.DEFAULT_LLM_MAX_OUTPUT_TOKENS

    @property
    def temperature(self) -> Union[float, None]:
        return self._temperature if self._temperature is not None else settings.DEFAULT_LLM_TEMPERATURE

    @property
    def connection_retry_count(self) -> Union[int, None]:
        return self._connection_retry_count if self._connection_retry_count is not None else settings.CONNECTION_RETRY_COUNT

    @property
    def prompt_retry_count(self) -> Union[int, None]:
        return self._prompt_retry_count if self._prompt_retry_count is not None else settings.PROMPT_RETRY_COUNT

    def merge_to_copy(self, secondary_options: Self) -> Self:
        merged_dict = {
            **{k: v for k, v in secondary_options.__dict__.items() if v is not None},
            **{k: v for k, v in self.__dict__.items() if v is not None}
        }

        return self.__class__(**{k[1:] if k.startswith('_') else k: v for k, v in merged_dict.items()})