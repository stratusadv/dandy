import importlib
import inspect
import sys
from pathlib import Path
from typing import Callable

from dandy import Prompt
from dandy.bot.bot import Bot
from dandy.cli.actions.action import BaseAction
from dandy.cli.intelligence.bots.source_code_bot import SourceCodeBot
from dandy.cli.session import session
from dandy.cli.tui.tui import tui
from dandy.file.utils import make_directory


class BotAction(BaseAction):
    name = 'Bot'
    description = 'Bots at your service!'
    calls = ('b', 'bot')

    def __init__(self) -> None:
        self.bots_path = Path(session.project_dandy_path, 'bots')

        make_directory(self.bots_path)

        self.sub_commands_methods: dict[str, Callable] = {
            'build': self.build_bot,
            'list': self.list_bots,
            'help': self.help,
            'run': self.run_bot,
        }

    @property
    def help_string(self) -> str:
        return f"""Usage: /bot run <BotName> [optional inline prompt]
        If no prompt, enter multi-line (end with /end).
        Other subcommands: {self.sub_commands_methods.keys()}
        """

    def build_bot(self, user_input: str) -> str:
        parts = user_input.split()

        if len(parts) < 2:
            bot_description = tui.get_user_input(question='Please describe the bot you want to build')
        else:
            bot_description = " ".join(parts[2:])

        start_time = tui.printer.start_task('Building', 'create a new bot')

        code_reference_prompt = (
            Prompt()
            .module_source('dandy.bot.bot')
            .lb()
            .module_source('dandy.llm.service')
            .lb()
            .module_source('dandy.file.service')
            .lb()
            .module_source('dandy.http.service')
            .lb()
            .module_source('dandy.intel.service')
            .lb()
            .sub_heading('Tutorials')
            .lb()
            .file(Path(session.project_base_path, 'docs', 'tutorials', 'bots.md'))
            .lb()
            .text('The file name for this code should be postfixed with `_bot` example `task_reviewer_bot.py`')
        )

        source_code_intel = SourceCodeBot().process(
            user_input=bot_description,
            code_reference_prompt=code_reference_prompt
        )

        source_code_intel.write_to_directory(self.bots_path)

        tui.printer.end_task(start_time)

        return f'Bot created at "{Path(self.bots_path, source_code_intel.file_name_with_extension)}"'

    def help(self) -> None:
        print(self.help_string)

    def list_bots(self, user_input: str) -> str:
        assert user_input
        return "Available bots:\n" + '\n'.join(self.bot_files) if self.bot_files else "No bots found."

    def run(self, user_input: str) -> str:
        parts = user_input.split()

        sub_command = parts[0].lower() if len(parts) > 0 else None

        if sub_command in self.sub_commands_methods:
            return self.sub_commands_methods[sub_command](
                user_input=user_input
            )

        return self.help_string

    def run_bot(self, user_input: str) -> str:
        parts = user_input.split()

        if len(parts) < 2:
            return "Error: Missing bot name. Usage: /bot run <BotName>"

        module_name = parts[1]

        # Add bots dir to sys.path for import
        sys.path.insert(0, str(self.bots_path))

        try:
            module = importlib.import_module(module_name)
        except ImportError as e:
            return f"Error: Could not import bot module '{module_name}.py' from {self.bots_path}: {e}"

        # Find the first Bot subclass in the module
        bot_class: type | None = None

        for _, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, Bot) and obj != Bot:
                bot_class: type = obj
                break

        if bot_class is None:
            return f"Error: No Bot subclass found in {module_name}.py"

        output = ''

        try:
            if issubclass(bot_class, Bot):
                bot_class().process()

                output = f'{bot_class.__name__} ran successfully!'
        except Exception as e:
            output = f"Bot failed with Error: {e}"

        return output

    @property
    def bot_files(self) -> list[str] | None:
        return [
            file.stem.replace('_bot', 'Bot').title()
            for file in self.bots_path.glob('*.py')
            if file.stem != '__init__'
        ]
