from dandy.bot.bot import Bot
from dandy.cli.actions.code.tools import CODE_EDITING_TOOLS
from dandy.intel.intel import DefaultIntel
from dandy.llm.prompt.prompt import Prompt


class CodingBot(Bot):
    role = 'Senior Software Engineer'
    task = (
        'Implement the user coding request by editing the project. '
        'Use the available tools to explore and modify the code, '
        'then give a short summary of what you changed and why.'
    )
    guidelines = (
        Prompt()
        .list([
            'All file and directory paths are relative to the project root.',
            'Read a file before editing it so you can match the exact text.',
            'Prefer edit_file for small targeted changes over rewriting the '
            'whole file with write_file.',
            'When choosing the old_string for edit_file, match the whitespace exactly.',
            'After making changes, verify them by reading the affected files again.',
        ])
    )

    def process(self, user_input: Prompt | str) -> DefaultIntel:
        return self.llm.tools.prompt_to_intel(
            prompt=user_input,
            tools=CODE_EDITING_TOOLS,
        )
