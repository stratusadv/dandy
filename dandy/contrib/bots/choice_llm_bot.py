from enum import Enum
from typing import Tuple, List, Union, overload, Type

from pydantic import BaseModel

from dandy.bot import LlmBot
from dandy.bot.exceptions import BotException
from dandy.llm.prompt import Prompt


NO_CHOICE_FOUND_RESPONSE = 'no-choice-match-found'


class SingleChoiceResponse(BaseModel):
    selected_choice: str


class MultipleChoiceResponse(BaseModel):
    selected_choices: List[str]


class _ChoiceLlmBot(LlmBot):
    role_prompt = (
        Prompt()
        .text('You are an intent bot.')
    )

    instructions_prompt = (
        Prompt()
        .text('Your job is to identify the intent of the user input and match it to one of the provided choices.')
        .text(f'If there is no good matches in the choices reply with value "{NO_CHOICE_FOUND_RESPONSE}".')
    )

    @classmethod
    def process(
            cls,
            user_input: str,
            choices: Union[Type[Enum], List[str], Tuple[str]],
            choice_response_model: Union[Type[SingleChoiceResponse], Type[MultipleChoiceResponse]]
    ) -> Union[SingleChoiceResponse, MultipleChoiceResponse]:

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
            choices: Union[List[str], Tuple[str]],
            choice_response_model: Type[BaseModel]
    ) -> Union[str, List[str], None]:
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
            choices: Union[Type[Enum], List[str], Tuple[str]],
            **kwargs
    ) -> Union[Enum, List[Enum], str, List[str], None]:
        ...


class SingleChoiceLlmBot(_ChoiceLlmBot, _ChoiceOverloadMixin):
    @classmethod
    def process(
            cls,
            user_input: str,
            choices: Union[Type[Enum], List[str], Tuple[str]],
            **kwargs
    ) -> Union[Enum, str, None]:

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
            else:
                return selected_choice


class MultipleChoiceLlmBot(_ChoiceLlmBot, _ChoiceOverloadMixin):
    @classmethod
    def process(
            cls,
            user_input: str,
            choices: Union[Type[Enum], List[str], Tuple[str]],
            **kwargs
    ) -> Union[List[Enum], List[str], None]:

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
            else:
                return select_choices
