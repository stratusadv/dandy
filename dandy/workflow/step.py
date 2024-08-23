from typing import Union, TYPE_CHECKING, Type

if TYPE_CHECKING:
    from dandy.llm.prompt import Prompt
    from dandy.agent import Agent
    from dandy.workflow.workflow import Workflow
    from dandy.tool import Tool
    from dandy.job.job import Job
    from dandy.schema import Schema


class Step:
    def __init__(
            self,
            name: str,
            handler: Union[
                Agent,
                Prompt,
                Tool,
                Workflow
            ],
            output_schema: Type[Schema],
            retries: int = 0
    ):
        self.name = name
        self.handler = handler
        self.output_schema = output_schema
        self.retries = retries

    def process(self, job: Job):
        pass