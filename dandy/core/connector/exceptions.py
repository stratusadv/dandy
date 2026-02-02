from dandy.core.exceptions import DandyCriticalError, DandyRecoverableError


class ConnectorCriticalError(DandyCriticalError):
    pass


class ConnectorRecoverableError(DandyRecoverableError):
    pass