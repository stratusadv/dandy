from dandy.domain.prompt.prompt import Prompt
from dandy.application.agent.cli.intelligence.prompts.path_prompt import _paths_section
from dandy.application.agent.cli.intelligence.prompts.tool_calling_prompt import (
    _tool_calling_section,
)
from dandy.application.agent.cli.intelligence.prompts.narration_prompt import _narration_section


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
