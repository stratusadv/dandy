from dandy.shared.exceptions import DandyCriticalError, DandyRecoverableError


class CacheCriticalError(DandyCriticalError):
    pass


class CacheRecoverableError(DandyRecoverableError):
    pass