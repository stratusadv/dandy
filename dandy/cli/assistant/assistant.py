from typing import Union

from dandy.cli import settings


def assistant(user_prompt: str) -> Union[str, None]:
    if user_prompt:
        user_input = user_prompt
    else:
        user_input = input(f'Assistant Prompt: ')

    return settings.DEFAULT_LLM_CONFIG.service.assistant_str_prompt_to_str(
        user_prompt_str=user_input
    )
