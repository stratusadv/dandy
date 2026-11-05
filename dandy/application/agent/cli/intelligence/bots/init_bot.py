from dandy.application.agent.cli.intelligence.prompts import init_guidelines_prompt
from dandy.application.agent.intelligence.tools import AGENT_TOOLS
from dandy.application.bot.bot import Bot
from dandy.shared.settings.load import get_cli_llm_config
from dandy.domain.intel.intel import DefaultIntel
from dandy.domain.prompt.prompt import Prompt


class InitBot(Bot):
    role = 'Project Documentation Engineer'

    def __post_init__(self) -> None:
        super().__post_init__()
        self.llm_config = get_cli_llm_config('CODING')
        self.guidelines = init_guidelines_prompt()

    task = (
        'Create or refresh the project AGENTS.md file: concise, factual guidance '
        'for AI coding agents working in this repository.'
    )

    def process(self, user_input: Prompt | str) -> DefaultIntel:
        return self.llm.tools.prompt_to_intel(prompt=user_input, tools=AGENT_TOOLS)
