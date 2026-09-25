from dandy.shared.exceptions import DandyCriticalError


class IntelCriticalError(DandyCriticalError):
    pass


class IntelRecoverableError(DandyCriticalError):
    pass