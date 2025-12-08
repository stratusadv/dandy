import sys

from dandy.cli.commands.command import BaseCommand


class QuitCommand(BaseCommand):
    name = 'Quit'
    description = 'Quit the application.'
    calls = ('q', 'quit')

    def help(self):
        print('Quit help')

    def run(self):
        print('Quitting...')
        sys.exit(0)
