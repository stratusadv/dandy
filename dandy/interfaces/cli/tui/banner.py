from pathlib import Path

from dandy.application.agent.session_store import SessionStore
from dandy.application.skill.loader import load_cli_skills
from dandy.domain.skill.skill import BaseSkill
from dandy.infrastructure.llm.config import LlmConfig
from dandy.shared.constants import AGENTS_MD_FILE_NAME
from dandy.shared.settings.load import get_cli_llm_config


def format_verbose_duration(seconds: float) -> str:
    """Humanize an elapsed duration for the completion sentence."""
    seconds = max(0.0, seconds)

    if seconds < 60:
        return f'{seconds:.1f} seconds'

    total_seconds = round(seconds)
    minutes, secs = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)

    parts: list[str] = []

    if hours:
        parts.append(f'{hours} hour{"s" if hours != 1 else ""}')

    if minutes:
        parts.append(f'{minutes} minute{"s" if minutes != 1 else ""}')

    if secs:
        parts.append(f'{secs} second{"s" if secs != 1 else ""}')

    return ''.join(parts) if len(parts) == 1 else ' and '.join(parts)


def agents_md_banner_line(project_base_path: Path) -> str:
    """The welcome banner line summarizing the project's AGENTS.md."""
    agents_md_path = Path(project_base_path, AGENTS_MD_FILE_NAME)

    if not agents_md_path.is_file():
        return 'not found - run /init to create one'

    size_bytes = agents_md_path.stat().st_size

    if size_bytes >= 1024:
        return f'found ({size_bytes / 1024:.1f} KB) - loaded into the agent system prompt'

    return f'found ({size_bytes} bytes) - loaded into the agent system prompt'


def agents_md_status(project_base_path: Path) -> str:
    """The short AGENTS.md status shown inside the welcome Config line."""
    if Path(project_base_path, AGENTS_MD_FILE_NAME).is_file():
        return 'AGENTS.md Found'

    return 'AGENTS.md Missing'


def config_banner_line(project_base_path: Path) -> str:
    """The welcome banner Config line: config + model, source file, AGENTS.md status."""
    config_name = get_cli_llm_config('CODING')
    model = LlmConfig(config_name).model

    return (
        f'{config_name} ({model}) [{settings_source_path()}] · '
        f'{agents_md_status(project_base_path)}'
    )


def settings_source_path() -> str:
    """The settings file path for the welcome banner.

    The `dandy.json` fallback file when settings loaded from JSON, the user
    settings module's file path when one resolves, or the module name alone
    when the module has no path (for example, `tests.dandy_settings`).
    """
    from dandy.shared.settings import settings  # noqa: PLC0415

    if settings._json_settings_path is not None:
        return str(settings._json_settings_path)

    user_settings = settings._user_settings

    if user_settings is not None:
        file_path = getattr(user_settings, '__file__', None)
        if file_path:
            return str(file_path)

        module_name = getattr(user_settings, '__name__', None)

        if module_name:
            return f'{module_name} module'

    return settings._settings_module_name or 'settings'


def session_banner_line(store: SessionStore) -> str:
    """The welcome banner line summarizing the project's saved sessions."""
    latest_name = store.latest()

    if latest_name is None:
        return 'none yet - the first turn is saved automatically'

    session_count = len(store.list_sessions())

    return f'{session_count} saved, latest: {latest_name} - resume with /r'


SKILL_BANNER_GROUP_LIMIT = 20


def _skill_group_names(skills: list[BaseSkill]) -> str:
    """Up to 20 skill names for one group, with `...` when the group is longer."""
    listed = [skill.name for skill in skills[:SKILL_BANNER_GROUP_LIMIT]]
    extra = len(skills) - len(listed)
    return ', '.join(listed) + ('...' if extra else '')


def skills_banner_line(project_base_path: Path) -> str:
    """The welcome banner line summarizing the skills loaded for the agent."""
    skills, _issues = load_cli_skills(project_base_path)

    if not skills:
        return 'none found - drop SKILL.md folders in .dandy/skills/'

    active_skills = [skill for skill in skills if skill.active]
    passive_skills = [skill for skill in skills if not skill.active]

    groups: list[str] = []

    if active_skills:
        groups.append(f'active: {_skill_group_names(active_skills)}')

    if passive_skills:
        groups.append(f'passive: {_skill_group_names(passive_skills)}')

    return f'{len(skills)} loaded ({", ".join(groups)})'
