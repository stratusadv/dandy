import argparse
from dataclasses import dataclass

from dandy.cli.commands.calculate_command import CalculateCommand
from dandy.cli.commands.command import BaseCommand
from dandy.processor.processor import BaseProcessor

COMMANDS: dict[str, BaseCommand] = {
    'calculate': CalculateCommand(),
}

@dataclass
class CommandLineInterface(BaseProcessor):
    def __init__(self):
        self.parser = argparse.ArgumentParser()

        for key, command in COMMANDS.items():
            sub_parser = self.parser.add_subparsers(dest='command')

            command_parser = sub_parser.add_parser(
                name=key,
                help=command.help,
            )

            command.add_arguments(command_parser)

    def process(self, *args, **kwargs):
        args = self.parser.parse_args()

        if args.command:
            COMMANDS[args.command].process(**vars(args))

        self.parser.print_help()

