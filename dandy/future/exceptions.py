from dandy.core.exceptions import DandyCriticalException, DandyRecoverableException


class FutureCriticalException(DandyCriticalException):
    pass


class FutureRecoverableException(DandyRecoverableException):
    pass