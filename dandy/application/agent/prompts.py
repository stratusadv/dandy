from dandy.domain.prompt.prompt import Prompt


def continuation_prompt() -> Prompt:
    return Prompt().text(
        'Continue working on the request. The conversation above contains the '
        'original request and your previous turns. Keep using your tools as '
        'needed. When the request is fully complete, set "done" to true in your '
        'response; otherwise keep "done" false and say what you did this turn '
        'and what remains.'
    )


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


def init_guidelines_prompt() -> Prompt:
    return (
        _paths_section()
        .sub_heading('Exploring the Project')
        .list(
            [
                'Start with list_directory on the project root to see the layout.',
                (
                    'Read the files that define how the project is built, run, and tested: '
                    'the manifest (pyproject.toml, package.json, go.mod, Cargo.toml, ...), '
                    'README, task runners (justfile, Makefile), CI config, and the test layout.'
                ),
                (
                    'Read entry points and a sample of the main modules to understand the '
                    'structure, but do not read every file -- be targeted.'
                ),
                'Use search_files to find where things live instead of guessing.',
            ]
        )
        .sub_heading('Writing AGENTS.md')
        .list(
            [
                (
                    'Write the complete final file to AGENTS.md (the project root) with one '
                    'write_file call; do not build it up with edit_file.'
                ),
                (
                    'Cover what an AI coding agent needs to work in this repository: '
                    'orientation (what the project is and where things live), essential '
                    'commands (build, test, lint, run), structure and conventions, and '
                    'non-obvious gotchas.'
                ),
                'Only document what you verified in the project; do not invent commands or paths.',
                'Keep it concise and factual -- no placeholders, no TODOs, no filler.',
                'Never include secrets, API keys, or credentials.',
            ]
        )
        .prompt(_narration_section(examples=['"Scanning the project layout to see what exists."']))
        .prompt(
            _tool_calling_section(
                never_paste_text=(
                    'Never paste file content or tool arguments as a javascript or JSON '
                    'code block in your message text.'
                )
            )
        )
        .sub_heading('Response Format')
        .list(['When you are done, give a short plain-text summary of what AGENTS.md covers.'])
    )


def init_prompt(existing_agents_md: str | None) -> Prompt:
    prompt = Prompt().text(
        'Create the project AGENTS.md file: concise, factual instructions for AI '
        'coding agents working in this repository.'
    )

    if existing_agents_md is not None:
        prompt = (
            prompt.text(
                'AGENTS.md already exists. Refresh it: keep what is still true, correct '
                'what is stale, drop what no longer applies, and add what is missing. '
                'Verify every kept claim against the project before writing.'
            )
            .text('The current AGENTS.md content is between the delimiter lines below.')
            .text('--- BEGIN CURRENT AGENTS.md ---')
            .text(existing_agents_md)
            .text('--- END CURRENT AGENTS.md ---')
        )

    return prompt


def session_name_prompt(request_text: str) -> Prompt:
    return (
        Prompt()
        .text(
            'Write a short title for this coding request: 8 to 10 words, title '
            'case, plain words only (no quotes, no trailing punctuation, no '
            'markdown, no code). The title becomes the session name.'
        )
        .text('The request is between the delimiter lines below.')
        .text('--- BEGIN REQUEST ---')
        .text(request_text)
        .text('--- END REQUEST ---')
        .sub_heading('Response Format')
        .list(
            [
                (
                    'Respond with raw JSON only. Do not wrap the JSON in markdown '
                    'code fences and do not add any other text around it.'
                )
            ]
        )
    )
