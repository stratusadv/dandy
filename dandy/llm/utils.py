from __future__ import annotations

from typing_extensions import TYPE_CHECKING, Union

from dandy.llm.service.prompts import service_system_prompt, service_user_prompt

if TYPE_CHECKING:
    from dandy.llm.prompt import Prompt


def get_estimated_token_count_for_prompt(
        prompt: Prompt,
        postfix_system_prompt: Union[Prompt, None] = None
) -> int:

    return service_system_prompt(
        system_prompt=postfix_system_prompt
    ).estimated_token_count + service_user_prompt(prompt).estimated_token_count