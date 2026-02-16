from dandy.cli.actions.action import BaseAction
from dandy.cli.actions.help.intelligence.bots.default_user_input_bot import DefaultUserInputBot
from dandy.cli.tui.tui import tui


class HelpAction(BaseAction):
    name = 'Help'
    description = 'Get help on how to use the Dandy command line interface.'
    calls = ('h', 'help')

    def help(self):
        print('help of all sorts')

    def run(self, user_input: str) -> str:
        start_time = tui.print_start_task('Generating', 'helpful answer')

        default_intel = DefaultUserInputBot().process(user_input)

        tui.print_end_task(start_time)

        return default_intel.response


    def render(self):
        print('Helping...')