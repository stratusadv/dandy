from dandy.core.exceptions import DandyCriticalError, DandyRecoverableError


class BotCriticalError(DandyCriticalError):
    pass


class BotRecoverableError(DandyRecoverableError):
    pass