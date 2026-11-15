from dandy.shared.exceptions import DandyExternalError, DandyUsageError


class LlmUsageError(DandyUsageError):
    pass


class LlmExternalError(DandyExternalError):
    pass
