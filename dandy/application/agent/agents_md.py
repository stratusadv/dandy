from pathlib import Path

from dandy.shared.files import file_exists, read_from_file
from dandy.domain.prompt.prompt import Prompt


def read_agents_md(agents_md_path: Path) -> str | None:
    """The project's AGENTS.md content, or None when the file is missing or blank."""
    if not file_exists(agents_md_path):
        return None

    agents_md = read_from_file(agents_md_path).strip()

    return agents_md or None


def agents_md_section(agents_md: str) -> Prompt:
    """The AGENTS.md content as a Project Instructions section for agent guidelines."""
    return (
        Prompt()
        .sub_heading('Project Instructions')
        .text(
            'The project provides the following instructions for AI coding agents. '
            'Follow them whenever they apply to your work.'
        )
        .text(agents_md)
    )
