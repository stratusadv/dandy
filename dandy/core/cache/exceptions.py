from dandy.core.exceptions import DandyCriticalException, DandyRecoverableException


class CacheCriticalException(DandyCriticalException):
    pass


class CacheRecoverableException(DandyRecoverableException):
    pass