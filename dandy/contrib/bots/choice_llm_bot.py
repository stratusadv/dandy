from abc import ABC
from enum import Enum
from typing_extensions import Tuple, List, Union, overload, Type, Dict

from pydantic import BaseModel

from dandy.bot import LlmBot
from dandy.bot.exceptions import BotException
from dandy.llm.prompt import Prompt


NO_CHOICE_FOUND_RESPONSE = 'no-choice-match-found'


class SingleChoiceResponse(BaseModel):
    selected_choice: str


class MultipleChoiceResponse(BaseModel):
    selected_choices: List[str]


class _ChoiceLlmBot(LlmBot, ABC):
    role_prompt = (
        Prompt()
        .text('You are an choice bot.')
    )

    @classmethod
    def process(
            cls,
            user_input: str,
            choices: Union[Type[Enum], List[str], Tuple[str], Dict[str, object]],
            choice_response_model: Union[Type[SingleChoiceResponse], Type[MultipleChoiceResponse]]
    ) -> Union[SingleChoiceResponse, MultipleChoiceResponse]:

        prompt = (
            Prompt()
            .text(user_input)
            .line_break()
            .text('These are the choices to pick from:')
        )

        if isinstance(choices, type) and issubclass(choices, Enum):
            prompt.array_random_order([choice.value for choice in choices])
        elif isinstance(choices, (list, tuple)):
            prompt.array_random_order(choices)
        elif isinstance(choices, dict):
            prompt.array_random_order(list(choices.keys()))
        else:
            raise BotException('Choices must be an Enum, a list or a tuple.')

        return cls.process_prompt_to_model_object(
            prompt=prompt,
            model=choice_response_model
        )


class _ChoiceOverloadMixin:
    @classmethod
    @overload
    def process(
            cls,
            user_input: str,
            choices: Dict[str, object],
            choice_response_model: Type[BaseModel]
    ) -> Union[Dict[str, object], None]:
        ...

    @classmethod
    @overload
    def process(
            cls,
            user_input: str,
            choices: Union[List[str], Tuple[str]],
            choice_response_model: Type[BaseModel]
    ) -> Union[str, List[Union[str, int, float, bool]], None]:
        ...

    @classmethod
    @overload
    def process(
            cls,
            user_input: str,
            choices: Type[Enum],
            choice_response_model: Type[BaseModel]
    ) -> Union[Enum, List[Enum], None]:
        ...

    @classmethod
    def process(
            cls,
            user_input: str,
            choices: Union[Type[Enum], List[str], Tuple[str], Dict[str, object]],
            **kwargs
    ) -> Union[Enum, List[Enum], str, List[Union[str, int, float, bool]], None]:
        ...


class SingleChoiceLlmBot(_ChoiceLlmBot, _ChoiceOverloadMixin):
    instructions_prompt = (
        Prompt()
        .text('Your job is to identify the intent of the user input and match it to the provided choices.')
        .text(f'If there is no good matches in the choices reply with value "{NO_CHOICE_FOUND_RESPONSE}".')
    )

    @classmethod
    def process(
            cls,
            user_input: str,
            choices: Union[Type[Enum], List[str], Tuple[str], Dict[str, object]],
            **kwargs
    ) -> Union[Enum, str, int, float, bool, Dict[str, object], None]:

        choice_response = super().process(
            user_input=user_input,
            choices=choices,
            choice_response_model=SingleChoiceResponse,
        )

        selected_choice = choice_response.selected_choice
        if selected_choice == NO_CHOICE_FOUND_RESPONSE:
            return None
        else:
            if isinstance(choices, type) and issubclass(choices, Enum):
                return choices(selected_choice)
            elif isinstance(choices, dict):
                return {selected_choice: choices[selected_choice]}
            else:
                return selected_choice


class MultipleChoiceLlmBot(_ChoiceLlmBot, _ChoiceOverloadMixin):
    instructions_prompt = (
        Prompt()
        .text('Your job is to identify the intent of the user input and match it to the provided choices.')
        .text('Return as many choices as you see relevant to the user input.')
        .text(f'If there is no good matches in the choices reply with value "{NO_CHOICE_FOUND_RESPONSE}".')
    )

    @classmethod
    def process(
            cls,
            user_input: str,
            choices: Union[Type[Enum], List[str], Tuple[str], Dict[str, object]],
            **kwargs
    ) -> Union[List[Enum], List[Union[str, int, float, bool]], Dict[str, object], None]:

        choice_response = super().process(
            user_input=user_input,
            choices=choices,
            choice_response_model=MultipleChoiceResponse
        )

        select_choices = choice_response.selected_choices
        if NO_CHOICE_FOUND_RESPONSE in select_choices:
            return None
        else:
            if isinstance(choices, type) and issubclass(choices, Enum):
                return [choices(choice) for choice in select_choices]
            elif isinstance(choices, dict):
                return {choice: choices[choice] for choice in select_choices}
            else:
                return select_choices
