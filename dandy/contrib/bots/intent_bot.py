from enum import Enum
from typing import Tuple, List, Union, overload, Type

from pydantic import BaseModel

from dandy.bot import LlmBot
from dandy.bot.exceptions import BotException
from dandy.llm.prompt import Prompt


class SingleChoiceResponse(BaseModel):
    selected_choice: str


class MultipleChoiceResponse(BaseModel):
    selected_choices: List[str]


class ChoiceIntentLlmBot(LlmBot):
    role_prompt = (
        Prompt()
        .text('You are an intent bot.')
    )

    instructions_prompt = (
        Prompt()
        .text('Your job is to identify the intent of the user input and match it to one of the provided choices.')
        .text('If there is no good matches in the choices reply with value "no-choice-match-found".')
    )

    @classmethod
    @overload
    def process(
            cls,
            user_input: str,
            choices: Union[List[str], Tuple[str]],
            multiple_responses: bool = False
    ) -> Union[str, List[str], None]:
        ...

    @classmethod
    @overload
    def process(
            cls,
            user_input: str,
            choices: Type[Enum],
            multiple_responses: bool = False
    ) -> Union[Enum, List[Enum], None]:
        ...

    @classmethod
    def process(
            cls,
            user_input: str,
            choices: Union[Type[Enum], List[str], Tuple[str]],
            multiple_responses: bool = False
    ) -> Union[Enum, List[Enum], str, List[str], None]:

        prompt = (
            Prompt()
            .text('This is the user input:')
            .text(user_input, triple_quote=True)
            .text('These are the choices:')
        )

        if isinstance(choices, type) and issubclass(choices, Enum):
            prompt.unordered_random_list([choice.value for choice in choices], triple_quote=True)
        elif isinstance(choices, (list, tuple)):
            prompt.unordered_random_list(choices, triple_quote=True)
        else:
            raise BotException('Choices must be an Enum, a list or a tuple.')

        response = cls.process_prompt_to_model_object(
            prompt=prompt,
            model=SingleChoiceResponse if not multiple_responses else MultipleChoiceResponse
        )

        if multiple_responses:
            select_choices = response.selected_choices
            if 'no-choice-match-found' in select_choices:
                return None
            else:
                if isinstance(choices, type) and issubclass(choices, Enum):
                    return [choices(choice) for choice in select_choices]
                else:
                    return select_choices

        else:
            selected_choice = response.selected_choice
            if selected_choice == 'no-choice-match-found':
                return None
            else:
                if isinstance(choices, type) and issubclass(choices, Enum):
                    return choices(selected_choice)
                else:
                    return selected_choice

