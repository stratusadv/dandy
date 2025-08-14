from dandy.core.connector.exceptions import ConnectorCriticalException, ConnectorRecoverableException


class HttpConnectorCriticalException(ConnectorCriticalException):
    pass


class HttpConnectorRecoverableException(ConnectorRecoverableException):
    pass