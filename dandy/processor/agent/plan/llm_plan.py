from pydantic import Field

from dandy.processor.agent.plan.plan import AgentPlanIntel
from dandy.processor.agent.plan.task.llm_task import LlmAgentTaskIntel
from dandy.llm.prompt.prompt import Prompt


class LlmAgentPlanIntel(AgentPlanIntel[LlmAgentTaskIntel]):
    tasks: list[LlmAgentTaskIntel] = Field(default_factory=list)

    def to_prompt(self) -> Prompt:
        prompt = Prompt()

        for order, task in enumerate(self.tasks, start=1):
            prompt.heading(f'Task {order}:')
            prompt.intel(task)

        return prompt