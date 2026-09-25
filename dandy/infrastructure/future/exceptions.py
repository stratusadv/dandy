from dandy.shared.exceptions import DandyCriticalError, DandyRecoverableError


class FutureCriticalError(DandyCriticalError):
    pass


class FutureRecoverableError(DandyRecoverableError):
    pass