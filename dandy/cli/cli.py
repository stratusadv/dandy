from pathlib import Path

from dandy.cli.actions.manager import ActionManager
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
        Tui.print_welcome()

        while True:
            user_input = self.newest_user_input

            if user_input is not None:
                user_input_words = user_input.split(' ')

                if user_input_words[0][0] == '/':

                    self.action_manager.call(
                        action=user_input_words[0][1:],
                        user_input=' '.join(user_input_words[1:]),
                    )

                else:
                    self.action_manager.call(
                        action='help',
                        user_input=' '.join(user_input_words),
                    )

            user_input = Tui.get_user_input(run_process_timer=False)

            self.user_inputs.append(user_input)

    @property
    def newest_user_input(self) -> str | None:
        return self.user_inputs[-1] if len(self.user_inputs) > 0 else None
