from dandy.core.exceptions import DandyCriticalException, DandyRecoverableException


class DebugCriticalException(DandyCriticalException):
    pass


class DebugRecoverableException(DandyRecoverableException):
    pass