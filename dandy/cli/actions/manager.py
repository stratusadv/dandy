from time import time, sleep

from dandy.cli.actions.constants import ACTIONS
from dandy.cli.actions.help.action import HelpAction
from dandy.cli.tui.tui import tui


class ActionManager:
    def __init__(self):
        self.calls_actions = {}

        actions = [*ACTIONS, HelpAction]

        for action in actions:
            for calls in action.calls:
                self.calls_actions[calls] = action

    def call(self, action: str, user_input: str):
        action = self.calls_actions.get(action)

        tui.printer.running_action(action)

        sleep(0.3)

        if action:
            start_time = time()

            result = action().run(
                user_input=user_input
            )

            tui.printer.completed_action(start_time, action)

            tui.printer.green_divider()

            tui.printer.output(result)

        else:
            print('Action not found')
