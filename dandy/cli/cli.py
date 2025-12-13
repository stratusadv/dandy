from pathlib import Path

from dandy.cli.commands.manager import CommandManager
from dandy.cli.intelligence.bots.default_user_input_bot import DefaultUserInputBot
from dandy.cli.tui.tui import Tui


class DandyCli:
    def __init__(self, current_working_directory: Path | str):
        self.cwd = Path(current_working_directory)
        self.command_manager = CommandManager()

    def run(self):
        user_input = None
        stop_timer = None
        Tui.print_welcome()

        while True:
            if user_input is not None:
                if user_input[0] == '/':
                    stop_timer()
                    self.command_manager.call(user_input[1:])
                else:
                    default_user_input_intel = DefaultUserInputBot().process(user_input)
                    print(default_user_input_intel.response)

            if stop_timer is not None:
                stop_timer()

            user_input, stop_timer = Tui.input()

