from typing import Type

from pydantic import BaseModel

from dandy.llm.prompt import Prompt


def ollama_model_prompt(model: Type[BaseModel]) -> Prompt:
    return (
        Prompt()
        .text('Response to the request above should be a JSON object that would validate against the following JSON Schema:')
        .line_break()
        .text('```')
        .model(model)
        .text('```')
    )


def ollama_system_prompt(user_prompt: Prompt, model: Type[BaseModel]) -> Prompt:
    return (
        Prompt()
        .text('Respond to the follow request:')
        .text('```')
        .prompt(user_prompt)
        .text('```')
        .line_break()
        .prompt(ollama_model_prompt(model))
    )
