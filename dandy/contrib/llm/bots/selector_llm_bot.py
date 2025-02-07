from typing_extensions import List

from dandy.intel import BaseIntel
from dandy.llm.bot.llm_bot import BaseLlmBot
from dandy.llm.prompt import Prompt


class SelectionIntel(BaseIntel):
    items: List[str]
    has_valid_choice: bool


class SelectorLlmBot(BaseLlmBot):
    intel_class = SelectionIntel
    
    instructions_prompt = (
        Prompt()
        .text('Be a helpful selector assistant that helps the user select from a list of choices. based on there input')
        .text('if no valid choice are in the list set the has_valid_choice to False')
    )

    @classmethod
    def process(
            cls,
            input_prompt: Prompt,
            choices: List[str],
            target_count: int = 1,
    ) -> SelectionIntel:
        
        prompt = Prompt()
        prompt.prompt(input_prompt)
        prompt.line_break()
        
        if target_count == 1:
            prompt.text(f'Use the following choices to pick a single value')
        else:
            prompt.text(f'Use the following choices to pick around {target_count} values:')
        
        prompt.list(choices)
        

        return cls.process_prompt_to_intel(prompt, cls.intel_class)
