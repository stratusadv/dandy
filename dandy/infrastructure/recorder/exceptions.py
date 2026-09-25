from dandy.shared.exceptions import DandyCriticalError, DandyRecoverableError


class RecorderCriticalError(DandyCriticalError):
    pass


class RecorderRecoverableError(DandyRecoverableError):
    pass