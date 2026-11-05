import traceback
from datetime import UTC, datetime
from pathlib import Path

from dandy.shared.constants import DANDY_LOCAL_DIRECTORY_NAME

_ERROR_LOGS_DIRECTORY_NAME = 'logs'
_ERROR_LOG_FILE_NAME = 'errors.log'
ERROR_LOG_MAX_LINES = 10000


def error_log_path(project_base_path: Path) -> Path:
    return Path(
        project_base_path,
        DANDY_LOCAL_DIRECTORY_NAME,
        _ERROR_LOGS_DIRECTORY_NAME,
        _ERROR_LOG_FILE_NAME,
    )


def log_cli_error(project_base_path: Path, context: str, error: BaseException) -> Path | None:
    """Append an error and its traceback to the project's CLI error log.

    The log lives at ``<project>/.dandy/logs/errors.log`` and is trimmed to
    the newest ``ERROR_LOG_MAX_LINES`` lines after each write. Writing is best
    effort: a failure to log never raises into the CLI, and ``None`` is
    returned when the entry could not be written.
    """
    try:
        log_path = error_log_path(project_base_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(UTC).astimezone().strftime('%Y-%m-%d %H:%M:%S')
        traceback_lines = ''.join(traceback.format_exception(error)).splitlines()
        entry_lines = [f'[{timestamp}] {context}', *traceback_lines]

        existing_lines = []
        if log_path.is_file():
            existing_lines = log_path.read_text(encoding='utf-8').splitlines()

        if existing_lines:
            existing_lines.append('')

        all_lines = existing_lines + entry_lines

        if len(all_lines) > ERROR_LOG_MAX_LINES:
            all_lines = all_lines[-ERROR_LOG_MAX_LINES:]

        with open(log_path, 'w', encoding='utf-8') as log_file:
            log_file.write('\n'.join(all_lines) + '\n')
    except Exception:
        return None

    return log_path
