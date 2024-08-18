from abc import ABC
from typing import Type, Any, TypeVar

from dandy.schema import Schema
from dandy.workflow.workflow import Workflow
from dandy.schema.type_vars import SchemaType


class Job(ABC):
    def __init__(
            self,
            input: Any,
            output_schema: Type[SchemaType],
            workflow: Type[Workflow],
    ):
        self.input = input
        self.output_schema = output_schema
        self.workflow = workflow

    def process(self) -> SchemaType:
        return self.workflow.process(self.input)
