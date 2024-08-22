from dandy.job.job import Job
from dandy.workflow.workflow import Workflow
from tests import agents

class BusinessIdeaEvaluationWorkflow(Workflow):
    agents = [
        agents.BusinessIdeaSWOTAgent,
        agents.BusinessMarketingAgent,
        agents.BusinessFinanceAgent,
    ]


