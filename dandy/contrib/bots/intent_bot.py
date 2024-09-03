from enum import Enum
from typing import Any, Tuple, List, Union, overload

from pydantic import BaseModel

from dandy.bot import LlmBot


class SingleChoiceResponse(BaseModel):
    selected_choice: str


class MultipleChoiceResponse(BaseModel):
    selected_choices: List[str]


class ChoiceIntentLlmBot(LlmBot):
    @classmethod
    @overload
    def process(
            cls,
            user_input: str,
            choices: Union[List[str], Tuple[str]],
            multiple_responses: bool = False
    ) -> str:
        ...

    @classmethod
    @overload
    def process(
            cls,
            user_input: str,
            choices: Enum,
            multiple_responses: bool = False
    ) -> Enum:
        ...

    @classmethod
    def process(
            cls,
            user_input: str,
            choices: Union[Enum, List[str], Tuple[str]],
            multiple_responses: bool = False
    ) -> Union[Enum, str]:
        if isinstance(choices, Enum):
            pass
        else:
            pass
