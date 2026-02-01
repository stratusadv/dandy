from dandy.core.exceptions import DandyCriticalError


class IntelCriticalError(DandyCriticalError):
    pass


class IntelRecoverableError(DandyCriticalError):
    pass