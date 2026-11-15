from dandy.shared.exceptions import DandyExternalError, DandyUsageError


class AgentUsageError(DandyUsageError):
    pass


class AgentExternalError(DandyExternalError):
    pass
