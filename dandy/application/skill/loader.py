from pathlib import Path

from dandy.domain.skill.skill import BaseSkill
from dandy.shared.constants import (
    DANDY_HOME_CONFIG_DIRECTORY_NAME,
    DANDY_LOCAL_DIRECTORY_NAME,
    SKILL_FILE_NAME,
    SKILLS_DIRECTORY_NAME,
)

FRONTMATTER_DELIMITER = '---'


def parse_skill_file(text: str) -> tuple[dict[str, str], str, list[str]]:
    """Split a SKILL.md into frontmatter fields, body, and parse issues.

    The frontmatter is a block of ``key: value`` lines between two ``---``
    fences at the very top of the file; the body is everything after the
    closing fence. Unknown keys are ignored. Returns the parsed fields, the
    body, and a list of issue strings - a missing/unclosed fence pair
    produces an issue and empty results.
    """
    lines = text.splitlines()
    issues: list[str] = []

    if not lines or lines[0].strip() != FRONTMATTER_DELIMITER:
        return {}, '', ['missing frontmatter opening "---" fence on the first line']

    closing_index = None

    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == FRONTMATTER_DELIMITER:
            closing_index = index
            break

    if closing_index is None:
        return {}, '', ['missing frontmatter closing "---" fence']

    frontmatter: dict[str, str] = {}

    for line in lines[1:closing_index]:
        if not line.strip():
            continue

        key, separator, value = line.partition(':')

        if not separator:
            issues.append(f'unrecognized frontmatter line: "{line.strip()}"')
            continue

        value = value.strip()

        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]

        frontmatter[key.strip()] = value

    body = '\n'.join(lines[closing_index + 1 :])

    return frontmatter, body, issues


def _parse_active(value: str) -> bool | None:
    if value.lower() in ('true', '1', 'yes'):
        return True

    if value.lower() in ('false', '0', 'no'):
        return False

    return None


def build_skill(skill_dir: Path, frontmatter: dict[str, str], body: str) -> BaseSkill:
    """Build a prompt-only BaseSkill from parsed frontmatter and a body.

    The name defaults to the skill folder name and ``active`` defaults to
    true; the markdown body is the skill prompt.
    """
    skill = BaseSkill(active=_parse_active(frontmatter.get('active', 'true')))
    skill.name = frontmatter.get('name') or skill_dir.name
    skill.description = frontmatter.get('description', '')
    skill.prompt = body.strip()
    skill.tools = []

    return skill


def load_skill_files(directories: list[Path]) -> tuple[list[BaseSkill], list[str]]:
    """Load prompt-only skills from ``<directory>/<skill-name>/SKILL.md`` files.

    Each skill is a folder holding a SKILL.md: the frontmatter supplies
    ``name`` (defaulting to the folder name), ``description``, and ``active``
    (defaulting to true); the markdown body is the skill prompt. Later
    directories override earlier ones by final skill name, so passing
    ``[global, project]`` gives the project skills the win. Nothing here
    raises: every failure becomes an issue string (path plus reason), and a
    missing or empty directory simply contributes no skills.
    """
    issues: list[str] = []
    loaded: dict[str, BaseSkill] = {}

    for directory in directories:
        if not directory.is_dir():
            continue

        for skill_dir in sorted(directory.iterdir()):
            skill_file = skill_dir / SKILL_FILE_NAME

            if not skill_dir.is_dir() or not skill_file.is_file():
                continue

            try:
                text = skill_file.read_text(encoding='utf-8')
            except OSError as error:
                issues.append(f'{skill_file}: could not be read ({error})')
                continue

            frontmatter, body, parse_issues = parse_skill_file(text)

            if parse_issues:
                issues.extend(f'{skill_file}: {issue}' for issue in parse_issues)
                continue

            name = frontmatter.get('name')

            if name is not None and not name:
                issues.append(f'{skill_file}: empty skill name')
                continue

            active_value = frontmatter.get('active', 'true')

            if _parse_active(active_value) is None:
                issues.append(f'{skill_file}: unrecognized "active" value: "{active_value}"')
                continue

            if not body.strip():
                issues.append(f'{skill_file}: empty skill prompt (markdown body)')
                continue

            skill = build_skill(skill_dir, frontmatter, body)

            if not skill.active and not skill.description:
                issues.append(f'{skill_file}: passive skill requires a description')
                continue

            loaded[skill.name] = skill

    return sorted(loaded.values(), key=lambda skill: skill.name), issues


def load_cli_skills(project_base_path: Path) -> tuple[list[BaseSkill], list[str]]:
    """Load the CLI skill directories: global, then project (project wins).

    The global directory is ``~/.config/dandy/skills/`` and the project
    directory is ``<project>/.dandy/skills/``.
    """
    global_skills_dir = (
        Path.home() / '.config' / DANDY_HOME_CONFIG_DIRECTORY_NAME / SKILLS_DIRECTORY_NAME
    )
    project_skills_dir = Path(project_base_path, DANDY_LOCAL_DIRECTORY_NAME, SKILLS_DIRECTORY_NAME)

    return load_skill_files([global_skills_dir, project_skills_dir])
