from dandy.core.exceptions import DandyCriticalException, DandyRecoverableException


class TypingCriticalException(DandyCriticalException):
    pass


class TypingRecoverableException(DandyRecoverableException):
    pass