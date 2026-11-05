from pathlib import Path

from dandy.shared.constants import AGENTS_MD_FILE_NAME
from dandy.application.agent.session_store import SessionStore


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


def session_banner_line(store: SessionStore) -> str:
    """The welcome banner line summarizing the project's saved sessions."""
    latest_name = store.latest()

    if latest_name is None:
        return 'none yet - the first turn is saved automatically'

    session_count = len(store.list_sessions())

    return f'{session_count} saved, latest: {latest_name} - resume it with /resume {latest_name}'
