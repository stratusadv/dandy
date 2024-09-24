from abc import ABC, abstractmethod
from typing import List, Self, Union

from dandy.bot import LlmBot


class LlmAgent(LlmBot, ABC):
    name: str
    agents: Union[List[Self], None] = None

    @classmethod
    @abstractmethod
    def process(cls, user_input: str) -> str:
        ...
