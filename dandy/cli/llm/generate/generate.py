from enum import Enum
from pathlib import Path

from typing_extensions import Union

from dandy.cli.llm.generate.intelligence.prompts.generate_llm_bot_prompts import generate_llm_bot_system_prompt, \
    generate_llm_bot_user_prompt
from dandy.intel import BaseIntel
from dandy.llm.service.config import BaseLlmConfig


class LlmBotSourceIntel(BaseIntel):
    file_name: str
    source: str


class GenerateChoices(Enum):
    LLM_BOT = 'llm_bot'


def generate(
        llm_config: BaseLlmConfig,
        choice: GenerateChoices,
        output_path: Union[Path, str],
        generate_description: Union[str, None] = None,
        output_to_file: bool = True
) -> None:

    if generate_description is None:
        generate_description = input('Describe what you want to generate: ')

    if choice == GenerateChoices.LLM_BOT:
        print(f'Generating {choice} ... depending on your llm configuration this may take up to a couple minutes')

        llm_bot_source_intel = llm_config.service.process_prompt_to_intel(
            prompt=generate_llm_bot_user_prompt(generate_description),
            intel_class=LlmBotSourceIntel,
            system_prompt=generate_llm_bot_system_prompt(),
        )

        if llm_bot_source_intel:
            if output_to_file:
                Path(output_path).mkdir(parents=True, exist_ok=True)

                with open(Path(output_path, llm_bot_source_intel.file_name), 'w') as f:
                    f.write(llm_bot_source_intel.source)

                print(f'Done ... saved to "{Path(output_path, llm_bot_source_intel.file_name)}"')

            else:
                print(llm_bot_source_intel.source)

        else:
            print('Failed to generate ... try again')
