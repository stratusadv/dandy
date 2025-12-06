from dandy.core.exceptions import DandyCriticalException, DandyRecoverableException


class FileCriticalException(DandyCriticalException):
    pass


class FileRecoverableException(DandyRecoverableException):
    pass
