class DandyError(Exception):
    pass


class DandyCriticalError(DandyError):
    pass


class DandyRecoverableError(DandyError):
    pass