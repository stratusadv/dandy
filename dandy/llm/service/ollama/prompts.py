from typing import Type, Optional

from pydantic import BaseModel

from dandy.llm.prompt import Prompt


def ollama_system_model_prompt(
        model: Type[BaseModel],
        prefix_system_prompt: Optional[Prompt] = None
) -> Prompt:
    prompt = Prompt()

    if isinstance(prefix_system_prompt, Prompt):
        prompt.prompt(prefix_system_prompt)

    prompt.text('You are a bot that helps users with all kinds of requests.')
    prompt.line_break()
    prompt.text('You must use the following rules when responding.')
    prompt.ordered_list([
        'Your response must be valid JSON.',
        'Your response must be valid according to the schema provided below.',
        'You will always respond with a JSON object with some values.',
    ])
    prompt.line_break()
    prompt.text('JSON Schema:')
    prompt.model(model, triple_quote=True)

    return prompt

def ollama_user_prompt(user_prompt: Prompt) -> Prompt:
    return (
        Prompt()
        .prompt(user_prompt)
    )
