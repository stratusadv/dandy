from random import randint
from typing import Self, Any

from pydantic import BaseModel

from dandy.conf import settings
from dandy.llm.exceptions import LlmCriticalException



class LlmOptions(BaseModel):
    frequency_penalty: float | None = None
    max_completion_tokens: int | None = None
    presence_penalty: float | None = None
    prompt_retry_count: int | None = 2
    temperature: float | None = None
    top_p: float | None = None

    class Config:
        extra = 'allow'

    def model_post_init(self, context: Any):
        VALUES_MIN_MAX = {
            'frequency_penalty': (-2.0, 2.0),
            'max_completion_tokens': (1, 99_999_999),
            'presence_penalty': (-2.0, 2.0),
            'prompt_retry_count': (0, 99),
            'temperature': (0.0, 2.0),
            'top_p': (0.0, 1.0),
        }

        for key, (min_value, max_value) in VALUES_MIN_MAX.items():
            value = getattr(self, key)

            if value is not None and (value < min_value or value > max_value):
                message = f'Invalid value for {key}: {value}. Must be between {min_value} and {max_value}'
                raise LlmCriticalException(message)

    # def __init__(
    #         self,
    #         seed: int | None = ...,
    #         randomize_seed: bool | None = ...,
    #         max_completion_tokens: int | None = ...,
    #         temperature: float | None = ...,
    #         prompt_retry_count: int | None = ...,
    # ):
    #
    #     self._seed = seed
    #     self._randomize_seed = randomize_seed
    #     self._max_completion_tokens = max_completion_tokens
    #     self._temperature = temperature
    #     self._prompt_retry_count = prompt_retry_count
    #
    # @property
    # def seed(self) -> int:
    #     if self._randomize_seed:
    #         return randint(0, 2**63 - 1)
    #
    #     return self._get_value_or_settings_default(
    #         self._seed,
    #         settings.LLM_DEFAULT_SEED
    #     )
    #
    # @seed.setter
    # def seed(self, value: int):
    #     self._seed = value
    #
    # @property
    # def randomize_seed(self) -> bool:
    #     return self._get_value_or_settings_default(
    #         self._randomize_seed,
    #         settings.LLM_DEFAULT_RANDOMIZE_SEED
    #     )
    #
    # @randomize_seed.setter
    # def randomize_seed(self, value: bool):
    #     self._randomize_seed = value
    #
    # @property
    # def max_completion_tokens(self) -> int:
    #     return self._get_value_or_settings_default(
    #         self._max_completion_tokens,
    #         settings.LLM_DEFAULT_MAX_COMPLETION_TOKENS
    #     )
    #
    # @max_completion_tokens.setter
    # def max_completion_tokens(self, value: int):
    #     self._max_completion_tokens = value
    #
    # @property
    # def temperature(self) -> float:
    #     return self._get_value_or_settings_default(
    #         self._temperature,
    #         settings.LLM_DEFAULT_TEMPERATURE
    #     )
    #
    # @temperature.setter
    # def temperature(self, value: float):
    #     self._temperature = value
    #
    # @property
    # def prompt_retry_count(self) -> int:
    #     return self._get_value_or_settings_default(
    #         self._prompt_retry_count,
    #         settings.LLM_DEFAULT_PROMPT_RETRY_COUNT
    #     )
    #
    # @prompt_retry_count.setter
    # def prompt_retry_count(self, value: int):
    #     self._prompt_retry_count = value
    #
    # @staticmethod
    # def _get_value_or_settings_default(value: Any, default: Any) -> Any:
    #     return value if value != ... else default
    #
    # def update_values(self, **kwargs):
    #     for key, value in kwargs.items():
    #         private_key = f'_{key}'
    #
    #         if hasattr(self, private_key) and value is not None:
    #             setattr(self, private_key, value)
    #
    # def merge_to_copy(self, secondary_options: Self) -> Self:
    #     """
    #     Merges the current instance with another secondary instance
    #     Current instance attributes that are not none will take precedence over the secondary instance
    #     """
    #
    #     merged_dict = {
    #         **{
    #             key: value
    #             for key, value in secondary_options.__dict__.items()
    #             if value is not None
    #         },
    #         **{key: value for key, value in self.__dict__.items() if value is not None},
    #     }
    #
    #     return self.__class__(
    #         **{
    #             key.removeprefix('_'): value
    #             for key, value in merged_dict.items()
    #         }
    #     )
