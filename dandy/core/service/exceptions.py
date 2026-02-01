from dandy.core.exceptions import DandyCriticalError, DandyRecoverableError


class ServiceCriticalError(DandyCriticalError):
    pass


class ServiceRecoverableError(DandyRecoverableError):
    pass