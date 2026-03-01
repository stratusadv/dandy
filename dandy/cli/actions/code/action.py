from time import sleep

from dandy.cli.actions.action import BaseAction
from dandy.cli.tui.tui import tui


class CodeAction(BaseAction):
    name = 'Code'
    description = 'Code something inside your project!'
    calls = ('c', 'Code')

    def help(self):
        print('Chat help')

    def run(self, user_input: str) -> str:
        if not user_input:
            user_input = tui.get_user_input(question='What would you like to code?')

        start_time = tui.printer.start_task('Coding', 'some sleepy time')

        sleep(1.0)

        tui.printer.end_task(start_time)

        return f'Coding {user_input}...'

    def render(self):
        print('hello')
