from dandy.core.exceptions import DandyCriticalError, DandyRecoverableError


class LlmCriticalError(DandyCriticalError):
    pass


class LlmValidationCriticalError(LlmCriticalError):
    def __init__(self):
        super().__init__('The format of the response from the LLM service war not processable.')


class LlmRecoverableError(DandyRecoverableError):
    pass
