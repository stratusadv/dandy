from dandy.core.exceptions import DandyCriticalException, DandyRecoverableException


class AgentCriticalException(DandyCriticalException):
    pass


class AgentRecoverableException(DandyRecoverableException):
    pass


class AgentOverThoughtRecoverableException(AgentRecoverableException):
    pass