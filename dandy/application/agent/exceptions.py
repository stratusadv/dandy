from dandy.shared.exceptions import DandyCriticalError, DandyRecoverableError


class AgentCriticalError(DandyCriticalError):
    pass


class AgentRecoverableError(DandyRecoverableError):
    pass
