from dandy.agent import Agent
from dandy.llm.prompt import Prompt


class WorkOrderComparisonAgent(Agent):
    role_prompt = (
        Prompt()
        .text('You\'re a work order comparison agent.')
    )

    instructions_prompt = (
        Prompt()
        .text('Your job is to look at a list of work orders and compare it to the provided work order')
    )


