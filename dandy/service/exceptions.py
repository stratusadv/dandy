from dandy.core.exceptions import DandyCriticalException, DandyRecoverableException


class ServiceCriticalException(DandyCriticalException):
    pass


class ServiceRecoverableException(DandyRecoverableException):
    pass