from time import sleep

import importlib
import inspect
import sys
from pathlib import Path

from dandy.bot.bot import Bot
from dandy.cli.actions.action import BaseAction
from dandy.cli.session import session
from dandy.cli.tui.tui import tui


class BotAction(BaseAction):
    name = 'Bot'
    description = 'Bots at your service!'
    calls = ('bot',)

    def help(self):
        # Simple help output (printed if called with no subcommand)
        return "Usage: /bot run <BotName> [optional inline prompt]\n" \
               "If no prompt, enter multi-line (end with /end). Other subcommands: list"

    def run(self, user_input: str) -> str:
        parts = user_input.split()
        if not parts:
            return self.help()

        subcmd = parts[0].lower()

        if subcmd == 'run':
            if len(parts) < 2:
                return "Error: Missing bot name. Usage: /bot run <BotName>"

            module_name = parts[1]
            bots_dir = Path(session.project_base_path) / '.dandy' / 'bots'

            if not bots_dir.exists():
                return f"Error: Bots directory not found at {bots_dir}. Create it first."

            # Add bots dir to sys.path for import
            sys.path.insert(0, str(bots_dir))

            try:
                module = importlib.import_module(module_name)
            except ImportError as e:
                return f"Error: Could not import bot module '{module_name}.py' from {bots_dir}: {e}"

            # Find the first Bot subclass in the module
            bot_class = None
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, Bot) and obj != Bot:
                    bot_class = obj
                    break

            if not bot_class:
                return f"Error: No Bot subclass found in {module_name}.py"

            bot_class().process()

            return 'Bot ran successfully!'

        elif subcmd == 'list':
            # Optional: List available bots
            bots_dir = Path(session.project_base_path) / '.dandy' / 'bots'
            if not bots_dir.exists():
                return "No bots directory found."
            bots = [f.stem.replace('_bot', 'Bot').title() for f in bots_dir.glob('*.py') if f.stem != '__init__']
            return "Available bots:\n" + '\n'.join(bots) if bots else "No bots found."

        else:
            return f"Unknown subcommand '{subcmd}'. Try 'run' or 'list'."

    def render(self):
        # Placeholder; not used in current CLI, but required
        pass