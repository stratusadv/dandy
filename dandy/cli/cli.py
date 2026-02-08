from pathlib import Path

from dandy.cli.actions.manager import ActionManager
from dandy.cli.intelligence.bots.default_user_input_bot import DefaultUserInputBot
from dandy.cli.tui.tui import Tui


class DandyCli:
    def __init__(self, current_working_directory: Path | str):
        self.cwd = Path(current_working_directory)
        self.action_manager = ActionManager()
        self.user_inputs = []

        # Setup autocomplete with all available action commands
        all_commands = list(self.action_manager.calls_actions.keys())
        Tui.setup_autocomplete(all_commands)

    def run(self):
        stop_timer = None
        Tui.print_welcome()

        while True:
            user_input = self.newest_user_input
            if user_input is not None:
                if user_input[0] == '/':
                    stop_timer()
                    self.action_manager.call(user_input[1:])
                else:
                    default_intel = DefaultUserInputBot().process(user_input)
                    stop_timer()
                    Tui.print(default_intel.response)

            if stop_timer is not None:
                stop_timer()

            user_input, stop_timer = Tui.input(run_process_timer=False)

            self.user_inputs.append(user_input)

    @property
    def newest_user_input(self) -> str | None:
        return self.user_inputs[-1] if len(self.user_inputs) > 0 else None