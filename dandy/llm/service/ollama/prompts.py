from typing import Type

from pydantic import BaseModel

from dandy.llm.prompt import Prompt


def ollama_system_model_prompt(model: Type[BaseModel]) -> Prompt:
    return (
        Prompt()
        .text('Respond to the user request with a JSON object that would validate against the following JSON Schema:')
        .model(model, triple_quote=True)
    )


def ollama_user_prompt(user_prompt: Prompt) -> Prompt:
    return (
        Prompt()
        .prompt(user_prompt)
    )
