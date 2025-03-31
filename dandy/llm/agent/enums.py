from enum import Enum


class AgentType(Enum):
    LEADER = 'leader'
    PLANNER = 'planner'
    EXECUTOR = 'executor'
    EVALUATOR = 'evaluator'