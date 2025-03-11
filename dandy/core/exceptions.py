class DandyException(Exception):
    pass


class DandyCriticalException(DandyException):
    pass


class DandyRecoverableException(DandyException):
    pass