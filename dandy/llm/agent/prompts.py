from typing_extensions import Type

from dandy.agent.plan.task.task import AgentTaskIntel
from dandy.agent.strategy import BaseAgentStrategy
from dandy.llm.prompt.prompt import Prompt


def agent_create_plan_prompt(
        user_prompt: Prompt,
        instructions_prompt: Prompt,
        strategy: Type[BaseAgentStrategy]
) -> Prompt:
    return (
        Prompt()
        .prompt(instructions_prompt)
        .line_break()
        .text('You need to create a plan with a set of tasks based on a given request by the user.')
        .text('Make sure to assign a strategy resource to each task created.')
        .line_break()
        .sub_heading('Strategy Resources')
        .dict(strategy.as_dict())
        .line_break()
        .prompt(user_prompt)
    )

def agent_do_task_prompt(
        task: AgentTaskIntel
) -> Prompt:
    return (
        Prompt()
        .text('Use the description and desired result to accomplish the task:')
        .line_break()
        .text(f'Description: {task.description}')
        .line_break()
        .text(f'Desired Result: {task.desired_result_description}')
        .line_break()
    )

