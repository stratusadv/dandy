from dandy.application.agent.agents_md import agents_md_section, read_agents_md
from dandy.application.agent.prompts import coding_guidelines_prompt
from dandy.application.agent.session import session
from dandy.application.agent.tools import AGENT_TOOLS
from dandy.application.bot.bot import Bot
from dandy.shared.settings.load import get_cli_llm_config
from dandy.domain.intel.intel import DefaultIntel
from dandy.domain.prompt.prompt import Prompt


class CodingBot(Bot):
    role = 'Senior Software Engineer'

    def __post_init__(self) -> None:
        super().__post_init__()
        self.llm_config = get_cli_llm_config('CODING')
        self.guidelines = self.build_guidelines()

    def build_guidelines(self) -> Prompt:
        guidelines = coding_guidelines_prompt()
        agents_md = read_agents_md(session.agents_md_path)

        if agents_md is not None:
            guidelines = guidelines.prompt(agents_md_section(agents_md))

        return guidelines

    task = (
        'Implement the user coding request by editing the project. '
        'Use the available tools to explore and modify the code, '
        'then give a short summary of what you changed and why.'
    )

    def process(self, user_input: Prompt | str) -> DefaultIntel:
        return self.llm.tools.prompt_to_intel(prompt=user_input, tools=AGENT_TOOLS)
