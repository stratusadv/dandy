from dandy.bot.bot import Bot
from dandy.cli.intelligence.prompts import coding_guidelines_prompt
from dandy.cli.intelligence.tools import AGENT_TOOLS
from dandy.cli.utils import get_cli_llm_config
from dandy.intel.intel import DefaultIntel
from dandy.llm.prompt.prompt import Prompt


class CodingBot(Bot):
    role = 'Senior Software Engineer'

    def __post_init__(self) -> None:
        super().__post_init__()
        self.llm_config = get_cli_llm_config('CODING')
        self.guidelines = coding_guidelines_prompt()

    task = (
        'Implement the user coding request by editing the project. '
        'Use the available tools to explore and modify the code, '
        'then give a short summary of what you changed and why.'
    )

    def process(self, user_input: Prompt | str) -> DefaultIntel:
        return self.llm.tools.prompt_to_intel(prompt=user_input, tools=AGENT_TOOLS)
