from pydantic import Field
from typing_extensions import Self, List

from dandy.agent.plan.task.task import BaseAgentTaskIntel
from dandy.intel import BaseIntel


class AgentPlan(BaseIntel):
    tasks: List[BaseAgentTaskIntel] = Field(default_factory=list)
    active_task_number: int = 0

    def __len__(self) -> int:
        return len(self.tasks)

    @property
    def active_task(self) -> BaseAgentTaskIntel:
        return self.tasks[self.active_task_number]

    def add_task_after_active(self, task: BaseAgentTaskIntel):
        self.tasks.insert(self.active_task_number + 1, task)
