from dandy.cli.agent.coding_agent import CodingAgent
from dandy.cli.tui.tui import tui

CLI_COMMANDS = ('clear', 'quit')


class DandyCli:
    def __init__(self) -> None:
        self.agent = CodingAgent()

    def process_user_input(self, user_input: str) -> bool:
        """Process one user input, returning False to stop the loop."""
        if user_input.startswith('/'):
            return self.process_command(user_input)

        self.process_agent_input(user_input)
        return True

    def process_command(self, user_input: str) -> bool:
        command = user_input.split(' ', 1)[0][1:].lower()

        if command == 'clear':
            self.agent.clear()
            tui.printer.output('Conversation cleared.')
            return True

        if command in {'exit', 'quit', 'q'}:
            return False

        tui.printer.error(
            error='Unknown command',
            description=f'"{command}" is not a valid command. Try {tuple(CLI_COMMANDS)}.',
        )
        return True

    def process_agent_input(self, user_input: str) -> None:
        tui.printer.running_phrase('Coding')

        try:
            result_intel = tui.printer.run_timed_task(
                action_name='Coding',
                task=user_input[:80],
                work=lambda update: self.agent.chat(user_input, progress_callback=update),
            )
        except Exception as error:
            tui.printer.error(error='Coding agent failed', description=str(error))
            return

        tui.printer.green_divider()
        tui.printer.output(result_intel.text)

    def run(self) -> None:
        tui.printer.welcome()

        while True:
            user_input = tui.get_user_input()

            if user_input is None:
                break

            if not self.process_user_input(user_input):
                break

        tui.printer.green_divider()
