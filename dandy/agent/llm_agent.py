from abc import ABC, abstractmethod
from typing import List, Self, Union, Type

from dandy.bot import LlmBot


class LlmAgent(LlmBot, ABC):
    agents: Union[List[Type[Self]], None] = None

    @classmethod
    @abstractmethod
    def process(cls, user_input: str) -> str:
        ...
