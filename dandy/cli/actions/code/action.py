from dandy.cli.actions.action import BaseAction
from dandy.cli.actions.code.intelligence.workflow import code_project_workflow
from dandy.cli.tui.tui import tui


class CodeAction(BaseAction):
    name = 'Code'
    description = 'Code something inside your project!'
    calls = ('c', 'code')

    def help(self) -> None:
        print(
            'Usage: /code <what you want to implement or change>\n'
            'Describe the change; the assistant explores the project with tools '
            'and edits the files directly.'
        )

    def run(self, user_input: str) -> str:
        if not user_input:
            user_input = tui.get_user_input(question='What would you like to code?')

        return code_project_workflow(
            user_input=user_input,
        )
