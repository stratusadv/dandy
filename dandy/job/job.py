from abc import ABC
from typing import Type, Any, TypeVar

from dandy.llm.prompt import Prompt
from dandy.workflow.workflow import Workflow
from dandy.schema.type_vars import SchemaType


class Job(ABC):
    def __init__(
            self,
            input_prompt: Prompt,
            output_schema: Type[SchemaType],
            workflow: Type[Workflow],
    ):
        self.input_prompt = input_prompt
        self.output_schema = output_schema
        self.workflow = workflow
        self.agent_output_schema_data = []

    def process(self) -> SchemaType:
        self.workflow.process(self)
