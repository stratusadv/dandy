from dandy.core.exceptions import DandyCriticalException, DandyRecoverableException


class BotCriticalException(DandyCriticalException):
    pass


class BotRecoverableException(DandyRecoverableException):
    pass