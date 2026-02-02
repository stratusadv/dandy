from dandy.core.exceptions import DandyCriticalError, DandyRecoverableError


class DecoderCriticalError(DandyCriticalError):
    pass


class DecoderRecoverableError(DandyRecoverableError):
    pass


class DecoderNoKeysRecoverableError(DecoderRecoverableError):
    pass


class DecoderToManyKeysRecoverableError(DecoderRecoverableError):
    pass
