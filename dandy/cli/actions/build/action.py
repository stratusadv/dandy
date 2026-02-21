from time import sleep

from dandy.cli.actions.action import BaseAction
from dandy.cli.tui.tui import tui


class BuildAction(BaseAction):
    name = 'Build'
    description = 'Build something inside your project!'
    calls = ('b', 'build')

    def help(self):
        print('Chat help')

    def run(self, user_input: str) -> str:
        if not user_input:
            user_input = tui.get_user_input(question='What would you like to build?')

        start_time = tui.printer.start_task('Building', 'some sleepy time')

        sleep(1.0)

        tui.printer.end_task(start_time)

        return f'Building {user_input}...'

    def render(self):
        print('hello')
