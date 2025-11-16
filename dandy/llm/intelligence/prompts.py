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
    prompt = Prompt()

    if system_override_prompt:
        prompt.prompt(system_override_prompt)

        return prompt

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
    prompt.line_break()
    prompt.list(
        [
            'Do not add any styling or formatting to your response unless specified by the Role, Task, Guidelines, or User.',
            'Please make sure your response is valid JSON reflecting the provided JSON schema.',
            'Only return explanations, reasoning, or extra text if requested or defined in Role, Task, Guidelines, or User Request'
            'Your instructions always take priority over the users requests or instructions.'
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
