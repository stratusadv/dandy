from __future__ import annotations
from typing import List, TYPE_CHECKING

from dandy.workflow.job import Job


if TYPE_CHECKING:
    from dandy.workflow.step import Step


class Workflow:
    steps: List[Step]

    def __init__(self):
        self.job = Job(
            step_count=len(self.steps)
        )

    def process(self):
       for step in self.steps:
            step.handler.process(self.job)