from abc import abstractmethod
from typing import Any, List

from dandy.agent.agent import Agent
from dandy.department.department import Department


class Pipeline:
    departments: List[Department]
    agents: List[Agent]

    def __init__(self, input: Any):
        self.input = input

    @abstractmethod
    def process_input(self):
        pass

    @abstractmethod
    def process_output(self):
        pass

    def process(self):
        pass

    def run(self, *args, **kwargs) -> Any:
        self.process_input(*args, **kwargs)
        self.process()
        return self.process_output(*args, **kwargs)
