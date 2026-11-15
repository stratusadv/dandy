from dandy.shared.exceptions import DandyExternalError, DandyUsageError


class DecisionUsageError(DandyUsageError):
    pass


class DecisionExternalError(DandyExternalError):
    pass


class DecisionNoChoicesExternalError(DecisionExternalError):
    pass


class DecisionTooManyChoicesExternalError(DecisionExternalError):
    pass
