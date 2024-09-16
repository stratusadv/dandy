from typing import List

from dandy.core.exceptions import DandyException


class LlmException(DandyException):
    pass


class LlmValidationException(LlmException):
    def __init__(self, name: str, choices: List[str]):
        super().__init__(f'Did not get a valid response format from llm service')