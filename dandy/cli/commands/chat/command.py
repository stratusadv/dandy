from dandy import Bot
from dandy.cli.commands.command import BaseCommand
from dandy.cli.tui.tui import Tui
from dandy.llm.conf import LlmConfigs


class ChatCommand(BaseCommand):
    name = 'Chat'
    description = f'Open ended chat to talk to the "{LlmConfigs().DEFAULT.model}" model for testing.'
    calls = ('c', 'chat', 'chizat')

    def help(self):
        print('Chat help')

    def run(self):
        user_input = Tui.input('Chat')
        response = Bot().process(user_input)
        print(response.text)
