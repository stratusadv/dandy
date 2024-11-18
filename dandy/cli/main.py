import argparse

from dandy.cli.generate.generate import GENERATE_CHOICES, generate
from dandy.cli.assistant.assistant import assistant
from dandy.cli import settings


def main():
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

            print(f'Done ... saved to "{settings.CURRENT_PATH / llm_bot_source.file_name}"')

        else:
            print('Failed to generate ... try again')


    elif args.assistant:
        print(f'Prompting Assistant ... depending on your llm configuration this may take up to a couple minutes')
        response = assistant(args.assistant)

        if response:
            print(response)

        else:
            print('Failed to get response from the assistant ... try again')

    else:
        parser.print_help()


if __name__ == '__main__':
    exit(main())
