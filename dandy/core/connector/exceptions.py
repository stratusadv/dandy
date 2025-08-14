from dandy.core.exceptions import DandyCriticalException, DandyRecoverableException


class ConnectorCriticalException(DandyCriticalException):
    pass


class ConnectorRecoverableException(DandyRecoverableException):
    pass