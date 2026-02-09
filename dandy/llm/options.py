from typing import Any

from pydantic import BaseModel, ConfigDict

from dandy.llm.exceptions import LlmCriticalError

_VALUES_MIN_MAX = {
    'frequency_penalty': (-2.0, 2.0),
    'max_completion_tokens': (1, 99_999_999),
    'presence_penalty': (-2.0, 2.0),
    'prompt_retry_count': (0, 99),
    'temperature': (0.0, 2.0),
    'top_p': (0.0, 1.0),
}


class LlmOptions(BaseModel):
    frequency_penalty: float | None = None
    max_completion_tokens: int | None = None
    presence_penalty: float | None = None
    prompt_retry_count: int | None = 2
    temperature: float | None = None
    top_p: float | None = None

    model_config = ConfigDict(
        extra='allow'
    )

    def model_post_init(self, context: Any):
        for key, (min_value, max_value) in _VALUES_MIN_MAX.items():
            value = getattr(self, key)

            if value is not None and (value < min_value or value > max_value):
                message = f'Invalid value for {key}: {value}. Must be between {min_value} and {max_value}'
                raise LlmCriticalError(message)
