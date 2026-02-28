import importlib
import inspect
import sys
from pathlib import Path
from typing import Callable

from dandy.bot.bot import Bot
from dandy.cli.actions.action import BaseAction
from dandy.cli.session import session
from dandy.file.utils import make_directory


class BotAction(BaseAction):
    name = 'Bot'
    description = 'Bots at your service!'
    calls = ('bot',)

    def __init__(self):
        self.bots_path = Path(session.project_dandy_path, 'bots')

        make_directory(self.bots_path)

        self.sub_commands_methods: dict[str, Callable] = {
            'build': self.build_bot,
            'list': self.list_bots,
            'help': self.help,
            'run': self.run_bot,
        }

    def build_bot(self, user_input: str) -> str:
        return f'Building "{user_input}"...'

    def help(self):
        return f"""Usage: /bot run <BotName> [optional inline prompt]
        If no prompt, enter multi-line (end with /end). 
        Other subcommands: {self.sub_commands_methods.keys()}
        """

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

        else:
            return self.help()

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

        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, Bot) and obj != Bot:
                bot_class: type = obj
                break

        if not bot_class:
            return f"Error: No Bot subclass found in {module_name}.py"

        try:
            bot_class().process()

            return f'{bot_class.__name__} ran successfully!'
        except Exception as e:
            message = f"Bot failed with Error: {e}"
            return message

    def render(self):
        # Placeholder; not used in current CLI, but required
        pass

    @property
    def bot_files(self) -> list[str] | None:
        return [
            file.stem.replace('_bot', 'Bot').title()
            for file in self.bots_path.glob('*.py')
            if file.stem != '__init__'
        ]
