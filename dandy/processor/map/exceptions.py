from dandy.core.exceptions import DandyCriticalException, DandyRecoverableException


class MapCriticalException(DandyCriticalException):
    pass


class MapRecoverableException(DandyRecoverableException):
    pass


class MapNoKeysRecoverableException(MapRecoverableException):
    pass


class MapToManyKeysRecoverableException(MapRecoverableException):
    pass
