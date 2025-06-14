from dandy.agent.plan.plan import AgentPlanIntel
from dandy.llm.prompt.prompt import Prompt


class LlmAgentPlanIntel(AgentPlanIntel):
    def to_prompt(self) -> Prompt:
        prompt = Prompt()

        for order, task in enumerate(self.tasks, start=1):
            prompt.heading(f'Task {order}:')
            prompt.intel(task)

        return prompt