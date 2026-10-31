from typing import Any

from pydantic import BaseModel, ConfigDict

from dandy.domain.request.exceptions import LlmCriticalError

_VALUES_MIN_MAX = {
    'frequency_penalty': (-2.0, 2.0),
    'presence_penalty': (-2.0, 2.0),
    'temperature': (0.0, 2.0),
    'top_p': (0.0, 1.0),
}

_VALUES_MIN = {
    'max_completion_tokens': 1,
    'max_tokens': 1,
    'n': 1,
    'top_logprobs': 0,
}


class LlmOptions(BaseModel):
    frequency_penalty: float | None = None
    logit_bias: dict[str, float] | None = None
    logprobs: bool | None = None
    max_completion_tokens: int | None = None
    max_tokens: int | None = None
    n: int | None = None
    presence_penalty: float | None = None
    reasoning_effort: str | None = None
    response_format: dict | None = None
    seed: int | None = None
    service_tier: str | None = None
    stop: str | list[str] | None = None
    temperature: float | None = None
    top_logprobs: int | None = None
    top_p: float | None = None

    model_config = ConfigDict(extra='allow')

    def model_post_init(self, context: Any):
        for key, (min_value, max_value) in _VALUES_MIN_MAX.items():
            value = getattr(self, key)

            if value is not None and (value < min_value or value > max_value):
                message = (
                    f'Invalid value for {key}: {value}. Must be between {min_value} and {max_value}'
                )
                raise LlmCriticalError(message)

        for key, min_value in _VALUES_MIN.items():
            value = getattr(self, key)

            if value is not None and value < min_value:
                message = f'Invalid value for {key}: {value}. Must be at least {min_value}.'
                raise LlmCriticalError(message)
