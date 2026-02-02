from dandy.core.exceptions import DandyCriticalError, DandyRecoverableError


class TypingCriticalError(DandyCriticalError):
    pass


class TypingRecoverableError(DandyRecoverableError):
    pass