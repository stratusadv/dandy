import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from dandy.application.agent.session import session
from dandy.domain.prompt.prompt import Prompt

_HIDDEN_TOP_LEVEL_NAMES = {'.git', '.dandy', '.venv', 'node_modules', '__pycache__', '.hypothesis'}
_GIT_COMMAND_TIMEOUT_SECONDS = 5
_MAX_TOP_LEVEL_ENTRIES = 50


def _git_project_info(project_base_path: Path) -> tuple[str, str] | None:
    """(branch, short dirty status) for the project repo, or None when unavailable."""
    if not (project_base_path / '.git').exists() or shutil.which('git') is None:
        return None

    git = shutil.which('git')

    def run_git(*arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [git, *arguments],
            cwd=project_base_path,
            capture_output=True,
            text=True,
            check=False,
            timeout=_GIT_COMMAND_TIMEOUT_SECONDS,
        )

    try:
        branch_result = run_git('rev-parse', '--abbrev-ref', 'HEAD')
        status_result = run_git('status', '--porcelain')
    except (OSError, subprocess.TimeoutExpired):
        return None

    if branch_result.returncode != 0 or not branch_result.stdout.strip():
        return None

    changed_count = len([line for line in status_result.stdout.splitlines() if line.strip()])
    status = 'clean' if changed_count == 0 else f'{changed_count} changed'

    return branch_result.stdout.strip(), status


def _top_level_listing(project_base_path: Path) -> str:
    try:
        entries = sorted(project_base_path.iterdir(), key=lambda entry: entry.name.lower())
    except OSError:
        return 'unavailable'

    names = [entry.name + '/' if entry.is_dir() else entry.name for entry in entries]
    names = [name for name in names if name.split('/')[0] not in _HIDDEN_TOP_LEVEL_NAMES]

    if len(names) > _MAX_TOP_LEVEL_ENTRIES:
        hidden_count = len(names) - _MAX_TOP_LEVEL_ENTRIES
        names = [*names[:_MAX_TOP_LEVEL_ENTRIES], f'... ({hidden_count} more)']

    return ', '.join(names) if names else '(empty)'


def collect_environment() -> dict[str, str]:
    """A snapshot of the host and project environment, for the coding agent prompt.

    Every lookup is bounded and failure-tolerant: a missing git repo or a
    vanished project root degrades the corresponding line instead of raising.
    """
    environment: dict[str, str] = {}

    environment['OS'] = platform.platform()
    environment['User'] = os.environ.get('USER') or os.environ.get('USERNAME') or 'unknown'
    environment['Python'] = platform.python_version()

    if sys.prefix != sys.base_prefix:
        environment['Python'] += f' (virtualenv: {sys.prefix})'

    environment['Project root'] = str(session.project_base_path)
    environment['Top level'] = _top_level_listing(session.project_base_path)

    for manifest_name in ('justfile', 'Justfile', 'makefile', 'Makefile'):
        if (session.project_base_path / manifest_name).is_file():
            environment['Build tooling'] = manifest_name
            break

    git_info = _git_project_info(session.project_base_path)

    if git_info:
        branch, status = git_info
        environment['Git'] = f'branch {branch}, {status}'
    else:
        environment['Git'] = 'not a git repository'

    return environment


def environment_section() -> Prompt:
    """The collected environment as a compact Environment section for agent guidelines."""
    return (
        Prompt()
        .sub_heading('Environment')
        .text('Snapshot of the working environment, captured when this conversation started.')
        .list([f'{key}: {value}' for key, value in collect_environment().items()])
    )
