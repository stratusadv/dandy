from dandy.shared.exceptions import DandyCriticalError, DandyRecoverableError


class BotCriticalError(DandyCriticalError):
    pass


class BotRecoverableError(DandyRecoverableError):
    pass