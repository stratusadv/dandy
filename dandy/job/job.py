from abc import ABC
from typing import Type, Any, TypeVar

from dandy.job.event import EventManager
from dandy.llm.prompt import Prompt
from dandy.schema import Schema
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
        self.events = EventManager()

    def process(self) -> SchemaType:
        return self.workflow.process(self.input)
