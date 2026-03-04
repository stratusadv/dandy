import sys

from dandy.cli.actions.action import BaseAction


class QuitAction(BaseAction):
    name = 'Quit'
    description = 'Quit the application.'
    calls = ('q', 'quit')

    def help(self) -> None:
        print('Quit help')

    def run(self, user_input: str) -> str:
        assert user_input
        sys.exit(0)
