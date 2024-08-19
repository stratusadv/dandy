from dandy.job.job import Job
from dandy.workflow.workflow import Workflow
from tests import agents

class BusinessIdeaEvaluationWorkflow(Workflow):
    agents = [
        agents.BusinessIdeaSWATAgent,
        agents.BusinessMarketingAgent,
        agents.BusinessFinanceAgent,
    ]

    @classmethod
    def process(cls, job: Job) -> Job:
        pass

