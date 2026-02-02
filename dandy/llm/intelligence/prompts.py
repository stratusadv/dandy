from pydantic import ValidationError

from dandy.core.utils import pydantic_validation_error_to_str
from dandy.llm.prompt.prompt import Prompt


def service_system_prompt(
    role: Prompt | str,
    task: Prompt | str | None = None,
    guidelines: Prompt | str | None = None,
    system_override_prompt: Prompt | str | None = None,
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
            'Do not add any styling, formatting, explanations, reasoning, or extra text to your response unless specified by your role, task, guidelines, or by the user\'s request.',
            'Your response must be valid JSON reflecting the provided JSON schema.',
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
        .text(f'{pydantic_validation_error_to_str(error)}', triple_backtick=True)
        .text(
            'Please review your response provide a valid JSON in your next response, based on the previous request.'
        )
    )