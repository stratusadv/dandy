from typing import List

from dandy.core.exceptions import DandyException


class LlmException(DandyException):
    pass


class LlmServiceNotFoundException(LlmException):
    def __init__(self, name: str, choices: List[str]):
        super().__init__(f'LLM service "{name}" is not setup, choices are: {", ".join(choices)}')