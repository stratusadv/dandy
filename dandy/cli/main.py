import sys
from pathlib import Path
from blessed import Terminal

CWD_PATH = Path.cwd()
term = Terminal()

sys.path.append(str(CWD_PATH))


def main():
    from dandy.cli.utils import check_or_create_settings, load_environment_variables

    load_environment_variables(CWD_PATH)
    check_or_create_settings(CWD_PATH)

    with term.fullscreen(), term.hidden_cursor(), term.cbreak():
        selected = 0
        options = ['Settings', 'Environment', 'Exit']

        while True:
            print(term.home + term.clear)
            print(term.bold_white('Dandy CLI'))
            print()

            for i, option in enumerate(options):
                if i == selected:
                    print(term.black_on_white(f'> {option}'))
                else:
                    print(f'  {option}')

            key = term.inkey()
            if key.is_sequence:
                if key.name == 'KEY_UP':
                    selected = (selected - 1) % len(options)
                elif key.name == 'KEY_DOWN':
                    selected = (selected + 1) % len(options)
            elif key == '\n':
                if selected == len(options) - 1:
                    return 0



if __name__ == '__main__':
    print(term.clear)
    with term.location(0, 0):
        print(term.bold_white('Starting Dandy CLI...'))
    sys.exit(main())
