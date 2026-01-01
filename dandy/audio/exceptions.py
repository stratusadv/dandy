from dandy.core.exceptions import DandyCriticalException, DandyRecoverableException


class AudioCriticalException(DandyCriticalException):
    pass


class AudioRecoverableException(DandyRecoverableException):
    pass