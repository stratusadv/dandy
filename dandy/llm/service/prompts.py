from typing import Type, Optional

from pydantic import BaseModel
from pydantic import ValidationError

from dandy.llm.prompt import Prompt


def service_system_model_prompt(
        model: Type[BaseModel],
        prefix_system_prompt: Optional[Prompt] = None
) -> Prompt:
    prompt = Prompt()

    if isinstance(prefix_system_prompt, Prompt):
        prompt.prompt(prefix_system_prompt)

    prompt.line_break()
    prompt.text('You must use the following rules when responding to the user.')
    prompt.ordered_list([
        'Your response must be valid JSON.',
        'Your response must be valid according to the JSON schema provided below.',
        'You will always respond with a JSON object with some values.',
    ])
    prompt.line_break()
    prompt.text('JSON Schema:')
    prompt.model_schema(model, triple_quote=True)

    return prompt


def service_system_validation_error_prompt(e: ValidationError) -> Prompt:
    return (
        Prompt()
        .text('The JSON response you provided was not valid.')
        .text('Here is the validation error provided by Pydantic when it tried to parse the JSON object:')
        .text(f'{e}', triple_quote=True)
        .text('Please provide a valid JSON object based on my earlier request.')
    )


def service_user_prompt(user_prompt: Prompt) -> Prompt:
    return (
        Prompt()
        .prompt(user_prompt)
    )


