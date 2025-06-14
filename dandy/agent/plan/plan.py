from pydantic import Field
from typing_extensions import List

from dandy.agent.plan.task.task import AgentTaskIntel
from dandy.intel import BaseIntel


class AgentPlanIntel(BaseIntel):
    tasks: List[AgentTaskIntel] = Field(default_factory=list)
    active_task_number: int = 0

    def __len__(self) -> int:
        return len(self.tasks)

    @property
    def active_task(self) -> AgentTaskIntel:
        return self.tasks[self.active_task_number]

    def set_active_task_complete(self):
        self.active_task.is_complete = True
        self.active_task_number += 1

    def add_task_after_active(self, task: AgentTaskIntel):
        self.tasks.insert(self.active_task_number + 1, task)
