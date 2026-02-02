from dandy.core.exceptions import DandyCriticalError, DandyRecoverableError


class FileCriticalError(DandyCriticalError):
    pass


class FileRecoverableError(DandyRecoverableError):
    pass
