from pydantic import ValidationError

from dandy.core.utils import pydantic_validation_error_to_str
from dandy.llm.prompt.prompt import Prompt
from dandy.llm.prompt.typing import PromptOrStrOrNone, PromptOrStr


def service_system_prompt(
    role: PromptOrStr,
    task: PromptOrStrOrNone = None,
    guidelines: PromptOrStrOrNone = None,
    system_override_prompt: PromptOrStrOrNone = None,
) -> Prompt:
    if system_override_prompt:
        return system_override_prompt

    prompt = Prompt()

    prompt.heading('Role')
    prompt.line_break()
    prompt.prompt(role)

    if task:
        prompt.line_break()
        prompt.heading('Task')
        prompt.line_break()
        prompt.prompt(task)

    if guidelines:
        prompt.line_break()
        prompt.heading('Guidelines')
        prompt.line_break()
        prompt.prompt(guidelines)

    prompt.line_break()
    prompt.heading('Constraints')
    prompt.list(
        [
            'Make sure your response is valid JSON reflecting the provided JSON schema.',
            'Do not use any markdown styling in your response.',
        ]
    )

    return prompt


def service_system_validation_error_prompt(error: ValidationError) -> Prompt:
    return (
        Prompt()
        .text(
            'The JSON in the response you provided was not valid based on the JSON schema that was provided.'
        )
        .text(
            'Here is the validation error provided by Pydantic when it tried to parse the JSON:'
        )
        .text(f'{pydantic_validation_error_to_str(error)}', triple_quote=True)
        .text(
            'Please review your response provide a valid JSON in your next response, based on the previous request.'
        )
    )


def service_user_prompt(user_prompt: PromptOrStr) -> Prompt:
    return Prompt().prompt(user_prompt)
