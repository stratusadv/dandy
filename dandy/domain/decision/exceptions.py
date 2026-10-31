from dandy.shared.exceptions import DandyCriticalError, DandyRecoverableError


class DecisionCriticalError(DandyCriticalError):
    pass


class DecisionRecoverableError(DandyRecoverableError):
    pass


class DecisionNoChoicesRecoverableError(DecisionRecoverableError):
    pass


class DecisionTooManyChoicesRecoverableError(DecisionRecoverableError):
    pass
