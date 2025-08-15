from dandy.core.exceptions import DandyCriticalException, DandyRecoverableException


class VisionCriticalException(DandyCriticalException):
    pass


class VisionRecoverableException(DandyRecoverableException):
    pass