from dandy.cli.commands.chat.command import ChatCommand
from dandy.cli.commands.command import BaseCommand
from dandy.cli.commands.explain.command import ExplainCommand
from dandy.cli.commands.quit.command import QuitCommand


class CommandManager:
    commands: tuple[BaseCommand, ...] = (
        ChatCommand,
        ExplainCommand,
        QuitCommand
    )

    def __init__(self):
        self.calls_commands = {}

        for command in self.commands:
            for calls in command.calls:
                self.calls_commands[calls] = command

    def call(self, command: str):
        command = self.calls_commands.get(command)
        if command:
            command().run()

        else:
            print('Command not found')
