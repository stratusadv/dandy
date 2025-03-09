from dandy.core.exceptions import DandyCriticalException, DandyRecoverableException


class LlmCriticalException(DandyCriticalException):
    pass


class LlmValidationCriticalException(LlmCriticalException):
    def __init__(self):
        super().__init__("Did not get a valid response format from llm service")


class LlmRecoverableException(DandyRecoverableException):
    pass