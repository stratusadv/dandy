from dandy.bot.bot import Bot
from dandy.cli.intelligence.tools import AGENT_TOOLS
from dandy.cli.utils import get_cli_llm_config
from dandy.intel.intel import DefaultIntel
from dandy.llm.prompt.prompt import Prompt


class CodingBot(Bot):
    role = 'Senior Software Engineer'

    def __post_init__(self) -> None:
        super().__post_init__()
        self.llm_config = get_cli_llm_config('CODING')

    task = (
        'Implement the user coding request by editing the project. '
        'Use the available tools to explore and modify the code, '
        'then give a short summary of what you changed and why.'
    )
    guidelines = Prompt().list(
        [
            'All file and directory paths are relative to the project root.',
            'Read a file before editing it so you can match the exact text.',
            (
                'Prefer edit_file for small targeted changes over rewriting the '
                'whole file with write_file.'
            ),
            'When choosing the old_string for edit_file, match the whitespace exactly.',
            'After making changes, verify them by reading the affected files again.',
            ('Use search_files to locate code instead of guessing or reading many files blindly.'),
            ('Use git_status and git_diff to check what has changed before and after editing.'),
            (
                'To run tests, linters, or other commands use run_command, but only '
                'when it is actually needed.'
            ),
            (
                'Begin every message that calls a tool with one short, natural sentence '
                'narrating the step you are about to take (for example, "Let me check the '
                'current git status." or "Reading the test file to understand it."). This '
                'narration is shown to the user as your running thoughts.'
            ),
        ]
    )

    def process(self, user_input: Prompt | str) -> DefaultIntel:
        return self.llm.tools.prompt_to_intel(prompt=user_input, tools=AGENT_TOOLS)
