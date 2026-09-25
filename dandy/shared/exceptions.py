class DandyError(Exception):
    pass


class DandyCriticalError(DandyError):
    pass


class DandyRecoverableError(DandyError):
    pass


class FileCriticalError(DandyCriticalError):
    pass


class FileRecoverableError(DandyRecoverableError):
    pass