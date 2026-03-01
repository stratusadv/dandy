from pathlib import Path

from dandy.cli.actions.manager import ActionManager
from dandy.cli.tui.tui import tui


class DandyCli:
    def __init__(self):
        self.action_manager = ActionManager()
        self.user_inputs = []

        tui.setup_autocomplete(
            list(
                self.action_manager.calls_actions.keys()
            )
        )

    def process_user_input(self, user_input: str):
        user_input_words = user_input.split(' ')

        if user_input_words[0][0] == '/':
            self.action_manager.call(
                action_key=user_input_words[0][1:],
                user_input=' '.join(user_input_words[1:]),
            )

        else:
            self.action_manager.call(
                action_key='help',
                user_input=' '.join(user_input_words),
            )

    def run(self):
        tui.printer.welcome()

        while True:
            user_input = self.newest_user_input

            if user_input is not None:
                self.process_user_input(user_input)

            user_input = tui.get_user_input()

            self.user_inputs.append(user_input)

    @property
    def newest_user_input(self) -> str | None:
        return self.user_inputs[-1] if len(self.user_inputs) > 0 else None
