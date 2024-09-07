from pydantic import ValidationError

from dandy.llm.prompt import Prompt


def pydantic_validation_error_prompt(e: ValidationError) -> Prompt:
    return (
        Prompt()
        .text('The JSON response you provided was not valid.')
        .text('Here is the validation error provided by Pydantic when it tried to parse the JSON:')
        .text(f'{e}', triple_quote=True)
        .text('Please provide a valid JSON object based on my earlier request.')
    )