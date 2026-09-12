from dandy.llm.prompt.prompt import Prompt


def _paths_section() -> Prompt:
    return (
        Prompt()
        .sub_heading('Paths')
        .list(['All file and directory paths are relative to the project root.'])
    )


def _narration_section(examples: list[str]) -> Prompt:
    return (
        Prompt()
        .sub_heading('Narration')
        .text(
            'Begin every message that calls a tool with one short, natural sentence '
            'narrating the step you are about to take. For example:',
            label='Narrate each tool call',
        )
        .list(examples, triple_backtick=True)
        .text('This narration is shown to the user as your running thoughts.')
    )


def _tool_calling_section(never_paste_text: str) -> Prompt:
    return (
        Prompt()
        .sub_heading('Calling Tools')
        .list(
            [
                (
                    'To perform an action, call the provided tool by name with its '
                    'arguments as a JSON object.'
                ),
                never_paste_text,
            ]
        )
    )


def coding_guidelines_prompt() -> Prompt:
    return (
        _paths_section()
        .sub_heading('Editing Code')
        .list(
            [
                'Read a file before editing it so you can match the exact text.',
                (
                    'Prefer edit_file for small targeted changes over rewriting the '
                    'whole file with write_file.'
                ),
                ('When choosing the old_string for edit_file, match the whitespace exactly.'),
                'After making changes, verify them by reading the affected files again.',
                (
                    'Use search_files to locate code instead of guessing or reading '
                    'many files blindly.'
                ),
                ('Use git_status and git_diff to check what has changed before and after editing.'),
                (
                    'To run tests, linters, or other commands use run_command, but only '
                    'when it is actually needed.'
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


def planning_guidelines_prompt() -> Prompt:
    return (
        _paths_section()
        .sub_heading('Planning Approach')
        .list(
            [
                'Keep the plan concise and focused on implementation steps.',
                'Identify specific files, functions, or classes that need changes.',
                'Order the steps logically so the coding bot can follow them sequentially.',
                'Do not implement anything -- only produce the plan.',
            ]
        )
        .prompt(
            _narration_section(
                examples=['"Scanning the project structure to find where things live."']
            )
        )
        .prompt(
            _tool_calling_section(
                never_paste_text=(
                    'Never paste tool arguments as a javascript or JSON code block '
                    'in your message text.'
                )
            )
        )
        .sub_heading('Response Format')
        .list(
            [
                (
                    'When you are done, respond with raw JSON only. Do not wrap the '
                    'JSON in markdown code fences and do not add any other text around it.'
                )
            ]
        )
    )
