from dandy.core.connector.exceptions import ConnectorCriticalError, ConnectorRecoverableError


class HttpConnectorCriticalError(ConnectorCriticalError):
    pass


class HttpConnectorRecoverableError(ConnectorRecoverableError):
    pass