from dandy.agent import Agent
from dandy.llm.prompt import Prompt


class BusinessIdeaSWOTAgent(Agent):
    role_prompt = (
        Prompt()
        .title('Your a business idea SWOT analyst')
        .text('You are an expert in business idea evaluation.')
    )

    instructions_prompt = (
        Prompt()
        .text('Your job is to evaluate a business idea and break it down into the following categories:')
        .unordered_random_list([
            'Strengths',
            'Weaknesses',
            'Opportunities',
            'Threats',
        ])
    )


class BusinessMarketingAgent(Agent):
    role_prompt = (
        Prompt()
        .title('Your a business marketing analyst')
        .text('You are an expert in business marketing evaluation.')
    )


class BusinessFinanceAgent(Agent):
    role_prompt = (
        Prompt()
        .title('Your a business finance analyst')
        .text('You are an expert in business finance evaluation.')
    )
