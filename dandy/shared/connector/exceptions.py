from dandy.shared.exceptions import DandyCriticalError, DandyRecoverableError


class ConnectorCriticalError(DandyCriticalError):
    pass


class ConnectorRecoverableError(DandyRecoverableError):
    pass