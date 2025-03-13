from dandy.core.exceptions import DandyCriticalException, DandyRecoverableException


class HttpCriticalException(DandyCriticalException):
    pass


class HttpRecoverableException(DandyRecoverableException):
    pass