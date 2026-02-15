from dandy.cli.actions.action import BaseAction
from dandy.cli.actions.explain.intelligence.workflow import explain_project_workflow
from dandy.cli.tui.tui import Tui


class ExplainAction(BaseAction):
    name = 'Explain'
    description = 'This will explain what the current project does.'
    calls = ('e', 'explain')

    def help(self):
        print('Chat help')

    def run(self, user_input: str):
        answer = explain_project_workflow(user_input)

        Tui.print(answer)

    def render(self):
        print('hello')
