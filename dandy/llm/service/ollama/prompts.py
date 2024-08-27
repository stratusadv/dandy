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

    prompt.text('Respond to the user request with a JSON object that would validate against the following JSON Schema:')
    prompt.model(model, triple_quote=True)

    return prompt

def ollama_user_prompt(user_prompt: Prompt) -> Prompt:
    return (
        Prompt()
        .prompt(user_prompt)
    )
