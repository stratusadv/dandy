from dandy.core.exceptions import DandyCriticalException


class IntelCriticalException(DandyCriticalException):
    pass


class IntelRecoverableException(DandyCriticalException):
    pass