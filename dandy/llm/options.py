from typing import Any

from pydantic import BaseModel

from dandy.llm.exceptions import LlmCriticalError


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
        self.validate_values()

    def validate_values(self):
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
                raise LlmCriticalError(message)

    # @staticmethod
    # def _get_value_or_settings_default(value: Any, default: Any) -> Any:
    #     return value if value != ... else default

    def update_values(self, **kwargs):
        for key, value in kwargs.items():
            if value is not None:
                setattr(self, key, value)

        self.validate_values()

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
