from dandy.processor.agent.plan.task.task import AgentTaskIntel
from dandy.llm.prompt.prompt import Prompt


class LlmAgentTaskIntel(AgentTaskIntel):
    def to_prompt(self) -> Prompt:
        return Prompt().intel(self)

