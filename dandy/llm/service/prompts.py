import json
from typing_extensions import Type, Union

from pydantic import ValidationError

from dandy.core.utils import pydantic_validation_error_to_str
from dandy.intel import BaseIntel
from dandy.llm.prompt import Prompt


def service_system_prompt(
        prefix_system_prompt: Union[Prompt, None] = None
) -> Prompt:
    prompt = Prompt()

    if isinstance(prefix_system_prompt, Prompt):
        prompt.prompt(prefix_system_prompt)

    return prompt


def service_system_validation_error_prompt(error: ValidationError) -> Prompt:
    return (
        Prompt()
        .text('The JSON response you provided was not valid.')
        .text('Here is the validation error provided by Pydantic when it tried to parse the JSON object:')
        .text(f'{pydantic_validation_error_to_str(error)}', triple_quote=True)
        .text('Please provide a valid JSON object based on my earlier request.')
    )


def service_user_prompt(user_prompt: Prompt) -> Prompt:
    return (
        Prompt()
        .prompt(user_prompt)
    )


