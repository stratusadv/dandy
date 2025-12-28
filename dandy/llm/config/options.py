from typing import Self, Any

from dandy.conf import settings
from dandy.llm.config.utils import generate_random_seed


class LlmConfigOptions:
    def __init__(
            self,
            seed: int | None = None,
            randomize_seed: bool | None = None,
            max_completion_tokens: int | None = None,
            temperature: float | None = None,
            prompt_retry_count: int | None = None,
    ):

        self._seed = seed
        self._randomize_seed = randomize_seed
        self._max_completion_tokens = max_completion_tokens
        self._temperature = temperature
        self._prompt_retry_count = prompt_retry_count

    @property
    def seed(self) -> int:
        if self._randomize_seed:
            return generate_random_seed()

        return self._seed if self._seed is not None else settings.LLM_DEFAULT_SEED

    @property
    def randomize_seed(self) -> bool:
        return self._get_value_or_settings_default(
            self._randomize_seed,
            settings.LLM_DEFAULT_RANDOMIZE_SEED
        )

    @property
    def max_completion_tokens(self) -> int:
        return self._get_value_or_settings_default(
            self._max_completion_tokens,
            settings.LLM_DEFAULT_MAX_COMPLETION_TOKENS
        )

    @property
    def temperature(self) -> float:
        return self._get_value_or_settings_default(
            self._temperature,
            settings.LLM_DEFAULT_TEMPERATURE
        )

    @property
    def prompt_retry_count(self) -> int:
        return self._get_value_or_settings_default(
            self._prompt_retry_count,
            settings.LLM_DEFAULT_PROMPT_RETRY_COUNT
        )

    @staticmethod
    def _get_value_or_settings_default(value: Any, default: Any) -> Any:
        return value if value is not None else default

    def update_values(self, **kwargs):
        for key, value in kwargs.items():
            private_key = f'_{key}'

            if hasattr(self, private_key) and value is not None:
                setattr(self, private_key, value)

    def merge_to_copy(self, secondary_options: Self) -> Self:
        """
        Merges the current instance with another secondary instance
        Current instance attributes that are not none will take precedence over the secondary instance
        """

        merged_dict = {
            **{
                key: value
                for key, value in secondary_options.__dict__.items()
                if value is not None
            },
            **{key: value for key, value in self.__dict__.items() if value is not None},
        }

        return self.__class__(
            **{
                key.removeprefix('_'): value
                for key, value in merged_dict.items()
            }
        )
