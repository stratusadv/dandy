from pydantic import ValidationError

from dandy.core.utils import pydantic_validation_error_to_str
from dandy.llm.prompt.prompt import Prompt
from dandy.llm.prompt.typing import PromptOrStrOrNone, PromptOrStr


def service_system_prompt(
        role: PromptOrStr,
        task: PromptOrStrOrNone = None,
        guidelines: PromptOrStrOrNone = None,
        system_override_prompt: PromptOrStrOrNone = None,
        postfix_system_prompt: PromptOrStrOrNone = None,
) -> Prompt:
    prompt = Prompt()

    prompt.sub_heading('Role')
    prompt.prompt(role)

    if task:
        prompt.line_break()
        prompt.sub_heading('Task')
        prompt.prompt(task)

    if guidelines:
        prompt.line_break()
        prompt.sub_heading('Guidelines')
        prompt.prompt(guidelines)

    prompt.line_break()
    prompt.sub_heading('Rules')
    if system_override_prompt:
        prompt.prompt(system_override_prompt)
    else:
        prompt.line_break()
        prompt.list([
            'Do not use any markdown styling in your response.',
        ])

    if postfix_system_prompt:
        prompt.line_break()
        prompt.prompt(postfix_system_prompt)

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