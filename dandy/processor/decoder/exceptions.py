from dandy.core.exceptions import DandyCriticalException, DandyRecoverableException


class DecoderCriticalException(DandyCriticalException):
    pass


class DecoderRecoverableException(DandyRecoverableException):
    pass


class DecoderNoKeysRecoverableException(DecoderRecoverableException):
    pass


class DecoderToManyKeysRecoverableException(DecoderRecoverableException):
    pass
