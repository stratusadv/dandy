import argparse

from pathlib import Path
import sys


CWD_PATH = Path.cwd()

sys.path.append(str(CWD_PATH))

def main():
    from dandy.cli.utils import check_or_create_settings, load_environment_variables

    check_or_create_settings(CWD_PATH)
    load_environment_variables(CWD_PATH)

    from dandy.utils import enum_to_list
    from dandy.llm.conf import llm_configs
    from dandy.cli.llm.generate.generate import GenerateChoices, generate
    from dandy.cli.llm.assistant.assistant import assistant
    from dandy.conf import settings
    from dandy.cli.llm.evaluate.evaluate import EvaluateChoices, evaluate
    from dandy.const import CLI_OUTPUT_DIRECTORY

    CLI_OUTPUT_PATH = Path(settings.BASE_PATH, CLI_OUTPUT_DIRECTORY)

    parser = argparse.ArgumentParser(description='Dandy CLI Tool')

    parser.add_argument(
        '-a', '--assistant',
        type=str,
        help='Prompt an a generic assistant to quickly test a prompt.',
    )

    parser.add_argument(
        '-e', '--evaluate',
        type=str,
        choices=enum_to_list(EvaluateChoices),
        help='Test an llm_bot.',
    )

    parser.add_argument(
        '-g', '--generate',
        type=str,
        choices=enum_to_list(GenerateChoices),
        help='Generate your selected choice by description into a source file.',
    )

    parser.add_argument(
        '-l', '--llm-config',
        dest='llm_config',
        type=str,
        choices=llm_configs.choices,
        default='DEFAULT',
        help='Select the llm config to use. Defaults to "DEFAULT".',
    )

    parser.add_argument(
        '-p', '--prompt',
        type=str,
        help='The string prompt to be used with the generate cli command.',
    )

    args = parser.parse_args()

    llm_config = llm_configs[args.llm_config]

    if args.assistant:
        assistant(
            llm_config=llm_config,
            user_prompt=args.prompt if args.prompt else args.assistant,
        )

    elif args.evaluate:
        evaluate(
            llm_config=llm_config,
            choice=EvaluateChoices(args.evaluate),
            module_and_obj=None,
            evaluate_description=args.prompt if args.prompt else None,
        )

    elif args.generate:
        generate(
            llm_config=llm_config,
            choice=GenerateChoices(args.generate),
            output_path=CLI_OUTPUT_PATH,
            generate_description=args.prompt if args.prompt else None,
        )

    else:
        parser.print_help()


if __name__ == '__main__':
    exit(main())
