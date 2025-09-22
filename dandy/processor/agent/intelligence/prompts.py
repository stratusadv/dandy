from dandy.processor.agent.plan.task.task import AgentTaskIntel
from dandy.processor.strategy import BaseProcessorsStrategy
from dandy.llm.prompt.prompt import Prompt
from dandy.llm.prompt.typing import PromptOrStr


def agent_create_plan_prompt(
        user_prompt: PromptOrStr,
        instructions_prompt: Prompt,
        processors_strategy: BaseProcessorsStrategy
) -> Prompt:
    return (
        Prompt()
        .prompt(instructions_prompt)
        .line_break()
        .text('Please create a good plan with a set of tasks to accomplish the given request by the user.')
        .text('Make sure to assign the mos relevant processor to each task created.')
        .line_break()
        .sub_heading('Processors')
        .dict(processors_strategy.as_dict())
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

