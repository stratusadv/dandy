from dandy.bot.bot import Bot
from dandy.cli.intelligence.tools import AGENT_TOOLS
from dandy.cli.utils import get_cli_llm_config
from dandy.intel.intel import DefaultIntel
from dandy.llm.prompt.prompt import Prompt


class PlanningBot(Bot):
    role = 'Planning Engineer'

    def __post_init__(self) -> None:
        super().__post_init__()
        self.llm_config = get_cli_llm_config('THINKING')

    task = (
        "Create a concise, actionable plan for implementing the user's coding request. "
        'Identify the key files and components that need to be modified or created, '
        'and outline the steps the coding bot should follow in order. '
        'Focus on clarity and practicality -- the plan should be something the coding bot '
        'can execute directly.'
    )
    guidelines = Prompt().list(
        [
            'All file and directory paths are relative to the project root.',
            'Keep the plan concise and focused on implementation steps.',
            'Identify specific files, functions, or classes that need changes.',
            'Order the steps logically so the coding bot can follow them sequentially.',
            'Do not implement anything -- only produce the plan.',
            (
                'When you are done, respond with raw JSON only. Do not wrap the '
                'JSON in markdown code fences and do not add any other text around it.'
            ),
        ]
    )

    def process(self, user_input: Prompt | str) -> DefaultIntel:
        return self.llm.tools.prompt_to_intel(prompt=user_input, tools=AGENT_TOOLS)
