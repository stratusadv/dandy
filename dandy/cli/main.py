import argparse

from dandy.cli.generate.generate import GENERATE_CHOICES, generate
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
        '-d', '--description',
        type=str,
        help='The description to be used with any cli commands.',
    )

    args = parser.parse_args()

    if args.generate:
        generate(choice=args.generate, description=args.description if args.description else None)

    else:
        parser.print_help()


if __name__ == '__main__':
    exit(main())
