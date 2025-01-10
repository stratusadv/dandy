from typing import Union

from dandy.llm.conf import llm_configs


def assistant(user_prompt: str) -> Union[str, None]:
    if user_prompt:
        user_input = user_prompt
    else:
        user_input = input(f'Assistant Prompt: ')

    return llm_configs.DEFAULT.service.assistant_str_prompt_to_str(
        user_prompt_str=user_input
    )
