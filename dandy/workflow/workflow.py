from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from dandy.workflow.step import Step
    from dandy.job.job import Job


class Workflow:
    steps: List[Step]

    def process(self, job: Job):
       for step in self.steps:
            step.process(job)