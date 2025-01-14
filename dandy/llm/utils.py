from __future__ import annotations

import traceback
from typing_extensions import TYPE_CHECKING, Type, Union

from dandy.core.type_vars import IntelType
from dandy.llm.service.prompts import service_system_intel_prompt, service_user_prompt

if TYPE_CHECKING:
    from dandy.llm.prompt import Prompt


def exception_to_str_nicely(ex: Exception) -> str:
    return '\n'.join([
        ''.join(traceback.format_exception_only(None, ex)).strip(),
        ''.join(traceback.format_exception(None, ex, ex.__traceback__)).strip()
    ])


def get_estimated_token_count_for_prompt(
        prompt: Prompt,
        intel_class: Type[IntelType],
        prefix_system_prompt: Union[Prompt, None] = None
) -> int:

    return service_system_intel_prompt(
        intel_class=intel_class,
        prefix_system_prompt=prefix_system_prompt
    ).estimated_token_count + service_user_prompt(prompt).estimated_token_count