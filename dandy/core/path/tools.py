from pathlib import Path
from typing import Sequence

from dandy.conf import settings
from dandy.core.exceptions import DandyCriticalException


def get_file_path_or_exception(
    file_path: str | Path,
) -> Path:
    if Path(file_path).is_file():
        return Path(file_path)

    if Path(settings.BASE_PATH, file_path).is_file():
        return Path(settings.BASE_PATH, file_path)

    message = f'File "{file_path}" does not exist'
    raise DandyCriticalException(message)


def get_dir_path_or_exception(
    dir_path: str | Path,
) -> Path:
    if Path(dir_path).is_dir():
        return Path(dir_path)

    if Path(settings.BASE_PATH, dir_path).is_dir():
        return Path(settings.BASE_PATH, dir_path)

    message = f'Directory "{dir_path}" does not exist'
    raise DandyCriticalException(message)


def get_dir_list(
    dir_path: str | Path,
    max_depth: int | None = None,
    file_extensions: Sequence[str] | None = None,
    _current_depth: int = 0,
) -> list[str]:
    if _current_depth == 0:
        file_extensions = _clean_file_extensions(file_extensions)

    items = []

    try:
        for path in dir_path.iterdir():
            if file_extensions is not None:
                if path.suffix in file_extensions:
                    items.append(str(path))
            else:
                items.append(str(path))

            if path.is_dir() and (max_depth is None or _current_depth < max_depth):
                items.extend(
                    get_dir_list(
                        path, max_depth, file_extensions, _current_depth + 1
                    )
                )

    except PermissionError:
        pass

    return items

def _clean_file_extensions(file_extensions: Sequence[str]) -> Sequence[str]:
    return [
        ext if ext[0:1] == '.' else f'.{ext}'
        for ext in file_extensions
    ]
