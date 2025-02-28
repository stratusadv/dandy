from dandy.core.exceptions import DandyException


class LlmException(DandyException):
    pass


class LlmValidationException(LlmException):
    def __init__(self):
        super().__init__("Did not get a valid response format from llm service")
