from dandy.processor.agent.intelligence.intel.task_intel import TaskIntel
from dandy.processor.agent.strategy import ProcessorsStrategy
from dandy.llm.prompt.prompt import Prompt
from dandy.llm.prompt.typing import PromptOrStr


def agent_create_plan_prompt(
        user_prompt: PromptOrStr,
        instructions_prompt: Prompt,
        processors_strategy: ProcessorsStrategy
) -> Prompt:
    return (
        Prompt()
        .prompt(instructions_prompt)
        .line_break()
        .text('Please create a thorough plan with a set of tasks to accomplish the provided request.')
        .text('Make sure to assign the most relevant processor to each task created.')
        .line_break()
        .sub_heading('Processors')
        .dict(processors_strategy.as_dict())
        .line_break()
        .prompt(user_prompt)
    )

def agent_do_task_prompt(
        task: TaskIntel
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

