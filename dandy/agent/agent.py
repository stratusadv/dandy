from abc import ABC

from dandy import config
from dandy.llm.prompt import Prompt
from dandy.agent.prompts import agent_process_job_prompt


class Agent(ABC):
    role_prompt: Prompt
    instructions_prompt: Prompt

    # @classmethod
    # def process(cls, job: Job):
    #     schema_data = config.active_llm_handler.process_prompt_to_schema(
    #         agent_process_job_prompt(cls.role_prompt, job.input_prompt),
    #         job.output_schema
    #     )
    #
    #     print(schema_data.to_json_nicely())
    #
    #     job.agent_output_schema_data.append(schema_data)
