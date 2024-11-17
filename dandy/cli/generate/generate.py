from typing import Union

from pydantic import BaseModel

from dandy.cli import settings
from dandy.cli.generate.intelligence.prompts.generate_llm_bot_prompts import generate_llm_bot_system_prompt, \
    generate_llm_bot_user_prompt


GENERATE_CHOICES = ['llmbot']

class LlmBotSource(BaseModel):
    file_name: str
    source: str


def generate(choice: str, description: Union[str, None] = None):
    if description:
        user_input = description
    else:
        user_input = input(f'Describe the {choice} you want to generate: ')

    print(f'Generating {choice} ... depending on your llm configuration this may take up to a couple minutes')

    if choice == 'llmbot':
        llm_bot_source = settings.DEFAULT_LLM_CONFIG.service.process_prompt_to_model_object(
            prompt=generate_llm_bot_user_prompt(user_input),
            model=LlmBotSource,
            prefix_system_prompt=generate_llm_bot_system_prompt(),
        )

        with open(llm_bot_source.file_name, 'w') as f:
            f.write(llm_bot_source.source)

        print(f'Done ... saved to "{settings.CURRENT_PATH / llm_bot_source.file_name}"')

