from typing_extensions import Self, List

from dandy.agent.plan.task.task import AgentTask


class AgentPlan:
    steps: List[Self, AgentTask]