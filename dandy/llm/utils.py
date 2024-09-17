from __future__ import annotations

import traceback
from typing import TYPE_CHECKING, Type, Optional

from dandy.core.type_vars import ModelType
from dandy.llm.service.prompts import service_system_model_prompt, service_user_prompt

if TYPE_CHECKING:
    from dandy.llm.prompt import Prompt


def exception_to_str_nicely(ex: Exception) -> str:
    return '\n'.join([
        ''.join(traceback.format_exception_only(None, ex)).strip(),
        ''.join(traceback.format_exception(None, ex, ex.__traceback__)).strip()
    ])


def lower_dict_keys(dictionary: dict) -> dict:
    return {k.lower(): v for k, v in dictionary.items()}


def get_estimated_token_count_for_prompt(
        prompt: Prompt,
        model: Type[ModelType],
        prefix_system_prompt: Optional[Prompt] = None) -> int:
    return service_system_model_prompt(
        model=model,
        prefix_system_prompt=prefix_system_prompt
    ).estimated_token_count + service_user_prompt(prompt).estimated_token_count