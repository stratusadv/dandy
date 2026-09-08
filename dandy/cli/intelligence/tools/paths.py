from pathlib import Path

from dandy.cli.session import session


def _resolve_project_path(relative_path: str) -> Path:
    root = session.project_base_path

    candidate = Path(relative_path) if relative_path else root

    resolved = candidate if candidate.is_absolute() else root / candidate
    resolved = resolved.resolve()
    root_resolved = root.resolve()

    if not resolved.is_relative_to(root_resolved):
        message = f'Path "{relative_path}" is outside the project at "{root_resolved}".'
        raise ValueError(message)

    return resolved


def _to_relative_path(path: Path) -> str:
    root = session.project_base_path.resolve()

    if path == root:
        return '.'

    return str(path.relative_to(root))
