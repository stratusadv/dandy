from typing_extensions import Self, List

from dandy.agent.plan.task.task import AgentTask


class AgentPlan:
    def __init__(self):
        self.tasks: List[AgentTask] = list()
        self.active_task_number: int = 0

    def __len__(self) -> int:
        return len(self.tasks)

    @property
    def active_task(self) -> AgentTask:
        return self.tasks[self.active_task_number]