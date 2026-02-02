from dandy.core.exceptions import DandyCriticalError, DandyRecoverableError


class FutureCriticalError(DandyCriticalError):
    pass


class FutureRecoverableError(DandyRecoverableError):
    pass