import sys
from pathlib import Path

from dandy.cli.commands.map import CALLS_COMMANDS
from dandy.cli.tui.tui import Tui
from dandy.llm.conf import llm_configs

CWD_PATH = Path.cwd()

sys.path.append(str(CWD_PATH))


def main():
    from dandy.cli.utils import check_or_create_settings, load_environment_variables

    load_environment_variables(CWD_PATH)
    check_or_create_settings(CWD_PATH)

    with Tui.term.fullscreen():
        command = None
        print(Tui.term.bold_blue('Welcome to Dandy CLI!'))
        print(Tui.term.bold_red('Using Model: ') + llm_configs.DEFAULT.model)

        while True:
            if command in CALLS_COMMANDS:
                print(CALLS_COMMANDS[command]().run())
            elif command is not None:
                print(f'You entered an invalid command: {command}')

            command = Tui.input()

            if command.lower() in ['/quit', '/q']:
                return 0


if __name__ == '__main__':
    Tui.clear()
    with Tui.term.location(0, 0):
        print(Tui.term.bold_white('Starting Dandy CLI...'))
    sys.exit(main())
