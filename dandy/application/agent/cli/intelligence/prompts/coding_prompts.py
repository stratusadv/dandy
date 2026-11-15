from dandy.application.agent.cli.intelligence.prompts.narration_prompt import _narration_section
from dandy.application.agent.cli.intelligence.prompts.path_prompt import _paths_section
from dandy.application.agent.cli.intelligence.prompts.tool_calling_prompt import (
    _tool_calling_section,
)
from dandy.domain.prompt.prompt import Prompt


def coding_task_prompt() -> Prompt:
    return Prompt(
        'Implement the user coding request by editing the project. '
        'Write understandable quality code, '
        'improve code structure, '
        'consider edge cases, '
        'validate your changes, '
        'and look for existing solutions in the project.'
        'Use the available tools to explore and modify the code, '
        'then give a short summary of what you changed and why.'
    )


def coding_guidelines_prompt(environment: Prompt | None = None) -> Prompt:
    guidelines = _paths_section()

    if environment is not None:
        guidelines = guidelines.prompt(environment)

    return (
        guidelines.sub_heading('Editing Code')
        .list(
            [
                'Read a file before editing it so you can match the exact text.',
                (
                    'Prefer edit_file for small targeted changes over rewriting the '
                    'whole file with write_file.'
                ),
                'When choosing the old_string for edit_file, match the whitespace exactly.',
                'After making changes, verify them by reading the affected files again.',
                (
                    'Use search_files to locate code instead of guessing or reading '
                    'many files blindly.'
                ),
                'Use git_status and git_diff to check what has changed before and after editing.',
                (
                    'To run tests, linters, or other commands use run_command, '
                    'but only when it is actually needed.'
                ),
                (
                    'Once the request is complete, stop calling tools and respond with '
                    'your final answer as plain text, never as a tool call.'
                ),
            ]
        )
        .prompt(
            _narration_section(
                examples=[
                    '"Let me check the current git status."',
                    '"Reading the test file to understand it."',
                ]
            )
        )
        .prompt(
            _tool_calling_section(
                never_paste_text=(
                    'Never paste tool arguments or your answer as a javascript or JSON '
                    'code block in your message text.'
                )
            )
        )
    )
