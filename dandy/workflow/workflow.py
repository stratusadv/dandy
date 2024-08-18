from abc import abstractmethod
from typing import Any, List, Optional

from dandy.agent.agent import Agent
from dandy.job.job import Job


class Workflow:
    agents: List[Agent]

    @classmethod
    @abstractmethod
    def process(cls, job: Job) -> Job:
       pass