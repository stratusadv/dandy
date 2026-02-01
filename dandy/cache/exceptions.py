from dandy.core.exceptions import DandyCriticalError, DandyRecoverableError


class CacheCriticalError(DandyCriticalError):
    pass


class CacheRecoverableError(DandyRecoverableError):
    pass