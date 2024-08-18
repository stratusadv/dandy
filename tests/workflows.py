from dandy.job.job import Job
from dandy.workflow.workflow import Workflow


class BusinessIdeaEvaluationWorkflow(Workflow):
    agents = []
    @classmethod
    def process(cls, job: Job) -> Job:
        pass

