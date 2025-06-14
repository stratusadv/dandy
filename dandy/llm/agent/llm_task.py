from dandy.agent.plan.task.task import AgentTaskIntel
from dandy.llm import Prompt


class LlmAgentTaskIntel(AgentTaskIntel):
    def to_prompt(self):
        return Prompt().intel(self)

