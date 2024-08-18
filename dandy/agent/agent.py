from abc import ABC, abstractmethod

from dandy.job.job import Job
from dandy.job.task.task import Task
from dandy.llm.prompt import Prompt
from dandy.schema import Schema


class Agent(ABC):
    role_prompt: Prompt

    @classmethod
    @abstractmethod
    def process(cls, job: Job) -> Job:
        pass