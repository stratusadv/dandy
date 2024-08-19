from dandy.agent import Agent
from dandy.job.job import Job
from dandy.llm.prompt import Prompt


class BusinessIdeaSWATAgent(Agent):
    role_prompt = (
        Prompt()
        .title('Your a business idea SWAT analyst')
        .text('You are an expert in business idea evaluation.')
    )

    @classmethod
    def process(cls, job: Job) -> Job:
        pass


class BusinessMarketingAgent(Agent):
    role_prompt = (
        Prompt()
        .title('Your a business marketing analyst')
        .text('You are an expert in business marketing evaluation.')
    )

    @classmethod
    def process(cls, job: Job) -> Job:
        pass


class BusinessFinanceAgent(Agent):
    role_prompt = (
        Prompt()
        .title('Your a business finance analyst')
        .text('You are an expert in business finance evaluation.')
    )

    @classmethod
    def process(cls, job: Job) -> Job:
        pass