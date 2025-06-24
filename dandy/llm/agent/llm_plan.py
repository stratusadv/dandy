from pydantic import Field
from typing_extensions import List

from dandy.agent.plan.plan import AgentPlanIntel
from dandy.llm.agent.llm_task import LlmAgentTaskIntel
from dandy.llm.prompt.prompt import Prompt


class LlmAgentPlanIntel(AgentPlanIntel[LlmAgentTaskIntel]):
    tasks: List[LlmAgentTaskIntel] = Field(default_factory=list)


    def to_prompt(self) -> Prompt:
        prompt = Prompt()

        for order, task in enumerate(self.tasks, start=1):
            prompt.heading(f'Task {order}:')
            prompt.intel(task)

        return prompt