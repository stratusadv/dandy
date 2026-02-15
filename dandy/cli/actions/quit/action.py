import sys

from dandy.cli.actions.action import BaseAction


class QuitAction(BaseAction):
    name = 'Quit'
    description = 'Quit the application.'
    calls = ('q', 'quit', 'exit')

    def help(self):
        print('Quit help')

    def run(self, user_input: str):
        sys.exit(0)

    def render(self):
        print('Quitting...')