from time import perf_counter, sleep, time

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

    def call(self, action_key: str, user_input: str):
        action = self.calls_actions.get(action_key)

        if action:
            tui.printer.running_action(action)

            sleep(0.3)

            start_time = perf_counter()

            result = action().run(
                user_input=user_input
            )

            tui.printer.completed_action(start_time, action)

            tui.printer.green_divider()

            tui.printer.output(result)

        else:
            tui.printer.error(
                error='Action not found',
                description=f'"{action_key}" is not a valid, choices are {tuple(self.calls_actions.keys())}',
            )

