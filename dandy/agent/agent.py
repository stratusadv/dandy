from abc import ABC

from dandy import config
from dandy.job.job import Job
from dandy.llm.prompt import Prompt
from dandy.agent.prompts import agent_process_job_prompt

class Agent(ABC):
    role_prompt: Prompt

    @classmethod
    def process(cls, job: Job) -> Job:
        config.active_llm_handler.process_prompt_to_schema(
            agent_process_job_prompt(cls.role_prompt, job.prompt),
            job.output_schema
        )
