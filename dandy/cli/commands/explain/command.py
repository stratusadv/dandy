from dandy import Bot, Prompt
from dandy.cli.commands.command import BaseCommand
from dandy.cli.commands.explain.intelligence.workflow import explain_project_workflow
from dandy.cli.tui.tui import Tui
from dandy.conf import settings


class ExplainCommand(BaseCommand):
    name = 'Explain'
    description = 'This will explain what the current project does.'
    calls = ('e', 'explain')

    def help(self):
        print('Chat help')

    def run(self):
        user_input, stop_timer = Tui.input('Explain')

        answer = explain_project_workflow(user_input)

        stop_timer()

        Tui.print(answer)

    def render(self):
        print('hello')