from dandy import Bot
from dandy.cli.commands.command import BaseCommand


class ChatCommand(BaseCommand):
    name = 'Chat'
    calls = ['chat']

    def help(self):
        print('Chat help')

    def run(self):
        response = Bot().process('Say something fun about Dandy')
        print(response.text)
