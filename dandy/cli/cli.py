from dandy.cli.commands.manager import CommandManager
from dandy.cli.intelligence.bots.default_user_input_bot import DefaultUserInputBot
from dandy.cli.tui.tui import Tui


class DandyCli:
    def __init__(self):
        self.command_manager = CommandManager()

    def run(self):
        user_input = None
        Tui.print_welcome()

        while True:
            if user_input is not None:
                if user_input[0] == '/':
                    self.command_manager.call(user_input[1:])
                else:
                    default_user_input_intel = DefaultUserInputBot().process(user_input)
                    print(default_user_input_intel.response)

            user_input = Tui.input()

