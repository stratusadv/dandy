from typing import Type

from dandy.llm.prompt import Prompt
from dandy.schema import Schema


def ollama_schema_prompt(schema_class: Type[Schema]) -> Prompt:
    return (
        Prompt()
        .title('Return a well formatted response exactly in the following valid JSON structure')
        .schema_with_types(schema_class)
    )


def ollama_system_prompt(user_prompt: Prompt, schema_class: Type[Schema]) -> Prompt:
    return (
        Prompt()
        .prompt(user_prompt)
        .line_break()
        .prompt(ollama_schema_prompt(schema_class))
    )