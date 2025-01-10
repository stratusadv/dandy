import argparse

from pathlib import Path
import sys

cwd_path = Path.cwd()

sys.path.append(str(cwd_path))

def main():
    from dandy.constants import DANDY_SETTINGS_FILE_NAME

    if not Path(cwd_path, DANDY_SETTINGS_FILE_NAME).exists():
        print(f'You need a "{DANDY_SETTINGS_FILE_NAME}" in your current directory.')
        return

    from dandy.cli.generate.generate import GENERATE_CHOICES, generate
    from dandy.cli.assistant.assistant import assistant
    from dandy.conf import settings
    from dandy.cli.test.test import test_handler

    parser = argparse.ArgumentParser(description='Dandy CLI')

    parser.add_argument(
        '-g', '--generate',
        type=str,
        choices=GENERATE_CHOICES,
        help='Generate your selected choice by description into a source file.',
    )

    parser.add_argument(
        '-a', '--assistant',
        type=str,
        help='Prompt an a generic assistant to quickly test a prompt.',
    )

    parser.add_argument(
        '-t', '--test',
        type=str,
        help='Test an llm_bot.',
    )

    parser.add_argument(
        '-p', '--prompt',
        type=str,
        help='The prompt to be used with the generate cli command.',
    )

    args = parser.parse_args()

    if args.generate:
        print(f'Generating {args.generate} ... depending on your llm configuration this may take up to a couple minutes')

        llm_bot_source = generate(choice=args.generate, description=args.prompt if args.prompt else None)

        if llm_bot_source:
            with open(llm_bot_source.file_name, 'w') as f:
                f.write(llm_bot_source.source)

            print(f'Done ... saved to "{settings.BASE_PATH / llm_bot_source.file_name}"')

        else:
            print('Failed to generate ... try again')


    elif args.assistant:
        print(f'Prompting Assistant ... depending on your llm configuration this may take up to a couple minutes')
        response = assistant(args.assistant)

        if response:
            print(response)

        else:
            print('Failed to get response from the assistant ... try again')

    elif args.test:
        test_handler(module_and_class=args.test, user_prompt=args.prompt if args.prompt else None)

    else:
        parser.print_help()


if __name__ == '__main__':
    exit(main())
