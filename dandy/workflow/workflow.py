from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from dandy.workflow.step import Step


class Workflow:
    steps: List[Step]

    def __init__(self):
        pass

    def process(self, job: 'Job'):
       for step in self.steps:
            step.process(job)