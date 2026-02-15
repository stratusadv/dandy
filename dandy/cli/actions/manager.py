from dandy.cli.actions.action import BaseAction
from dandy.cli.actions.explain.action import ExplainAction
from dandy.cli.actions.quit.action import QuitAction


class ActionManager:
    actions: tuple[BaseAction, ...] = (
        ExplainAction,
        QuitAction
    )

    def __init__(self):
        self.calls_actions = {}

        for action in self.actions:
            for calls in action.calls:
                self.calls_actions[calls] = action

    def call(self, action: str, user_input: str):
        action = self.calls_actions.get(action)

        if action:
            action().run(
                user_input=user_input
            )

        else:
            print('Action not found')
