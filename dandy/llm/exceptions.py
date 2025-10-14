from dandy.core.exceptions import DandyCriticalException, DandyRecoverableException


class LlmCriticalException(DandyCriticalException):
    pass


class LlmValidationCriticalException(LlmCriticalException):
    def __init__(self):
        super().__init__("The format of the response from the LLM service war not processable.")


class LlmRecoverableException(DandyRecoverableException):
    pass
