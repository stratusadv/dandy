from abc import ABC
from enum import Enum
from typing_extensions import Tuple, List, Union, overload, Type, Dict, Any

from dandy.intel.type_vars import IntelType
from dandy.llm.bot import LlmBot
from dandy.bot.exceptions import BotException
from dandy.intel import Intel
from dandy.llm.intel import DefaultLlmIntel
from dandy.llm.prompt import Prompt


class SelectedValuesIntel(Intel):
    items: List[str]
    valid_choice_found: bool


class ValueSelectorLlmBot(LlmBot):
    instructions_prompt = (
        Prompt()
        .text('Be a helpful value picker')
    )

    @classmethod
    def process_from_dict(cls, input_prompt: Prompt, input_dict: Dict, target_choices: int = 1) -> List[Any]:
        prompt = (
            Prompt()
            .prompt(input_prompt)
            .line_break()
            .text(f'Use the following choices to pick at least {target_choices} value:')
            .list(list(input_dict.keys()))
        )
        
        selected_values = cls.process(prompt, SelectedValuesIntel)
        
        return [input_dict[item] for item in selected_values.items]
