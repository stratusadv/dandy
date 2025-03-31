from dandy.core.exceptions import DandyCriticalException, DandyRecoverableException


class RecorderCriticalException(DandyCriticalException):
    pass


class RecorderRecoverableException(DandyRecoverableException):
    pass