from dandy.cli.actions.action import BaseAction
from dandy.cli.tui.tui import tui


class BuildAction(BaseAction):
    name = 'Build'
    description = 'Build something inside your project!'
    calls = ('b', 'build')

    def help(self):
        print('Chat help')

    def run(self, user_input: str) -> str:
        tui.get_user_input(question='What would you like to build?')

        return f'Building {user_input}...'

    def render(self):
        print('hello')
