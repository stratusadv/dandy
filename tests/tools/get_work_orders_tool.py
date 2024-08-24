from dandy.workflow.job import Job
from dandy.tool.tool import Tool


class GetWorkOrdersTool(Tool):
    def process(self, job: Job, ) -> Job:
        return job