from time import time

from pydantic import Field, PrivateAttr
from typing import Any

from dandy.llm.prompt.prompt import Prompt
from dandy.intel.intel import BaseIntel
from dandy.processor.agent.intelligence.intel.task_intel import TaskIntel


class PlanIntel(BaseIntel):
    tasks: list[TaskIntel] = Field(default_factory=list)
    _plan_time_limit_seconds: int = 0
    _active_task_index: int = 0
    _plan_start_time: float = PrivateAttr(default_factory=time)

    def __len__(self) -> int:
        return len(self.tasks)

    def model_post_init(self, __context: Any, /):
        self.set_task_numbers()

    @property
    def active_task(self) -> TaskIntel:
        return self.tasks[self._active_task_index]

    @property
    def active_task_number(self) -> int:
        return self._active_task_index + 1

    def add_task_after_active(self, task_intel: TaskIntel):
        self.tasks.insert(self._active_task_index + 1, task_intel)
        self.set_task_numbers()

    @property
    def has_exceeded_time_limit(self) -> bool:
        if self._plan_time_limit_seconds == 0:
            return False

        return time() - self._plan_start_time > self._plan_time_limit_seconds

    @property
    def is_complete(self) -> bool:
        return False not in [task.is_complete for task in self.tasks]

    @property
    def is_incomplete(self) -> bool:
        return not self.is_complete

    def set_active_task_complete(self):
        self.active_task.is_complete = True
        self._active_task_index += 1

    def set_plan_time_limit(self, seconds: int):
        self._plan_time_limit_seconds = seconds

    def set_task_numbers(self):
        for index, task in enumerate(self.tasks, start=1):
            task.number = index

    def to_prompt(self) -> Prompt:
        prompt = Prompt()

        for order, task_intel in enumerate(self.tasks, start=1):
            prompt.heading(f'Task {order}:')
            prompt.intel(task_intel)

        return prompt
