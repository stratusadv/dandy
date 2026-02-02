from __future__ import annotations

import base64
from pathlib import Path
from typing import Sequence
from urllib.parse import urlparse

from dandy.core.exceptions import DandyCriticalError
from dandy.conf import settings


def append_to_file(file_path: Path | str, content: str):
    if file_exists(file_path):
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(content)

    else:
        write_to_file(file_path, content)


def clean_file_extensions(file_extensions: Sequence[str]) -> Sequence[str]:
    return [
        ext if ext[0:1] == '.' else f'.{ext}'
        for ext in file_extensions
    ]


def encode_file_to_base64(file_path: str | Path) -> str:
    if not Path(file_path).is_file():
        message = f'File "{file_path}" does not exist'
        raise DandyCriticalError(message)

    with open(file_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


def file_exists(file_path: Path | str) -> bool:
    return Path(file_path).exists()


def get_file_path_or_exception(
        file_path: str | Path,
) -> Path:
    if Path(file_path).is_file():
        return Path(file_path)

    if Path(settings.BASE_PATH, file_path).is_file():
        return Path(settings.BASE_PATH, file_path)

    message = f'File "{file_path}" does not exist'
    raise DandyCriticalError(message)


def get_directory_path_or_exception(
        dir_path: str | Path,
) -> Path:
    if Path(dir_path).is_dir():
        return Path(dir_path)

    if Path(settings.BASE_PATH, dir_path).is_dir():
        return Path(settings.BASE_PATH, dir_path)

    message = f'Directory "{dir_path}" does not exist'
    raise DandyCriticalError(message)


def get_directory_listing(
        dir_path: str | Path,
        max_depth: int | None = None,
        file_extensions: Sequence[str] | None = None,
        _current_depth: int = 0,
) -> list[str]:
    if _current_depth == 0 and file_extensions is not None:
        file_extensions = clean_file_extensions(file_extensions)

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
                    get_directory_listing(
                        path, max_depth, file_extensions, _current_depth + 1
                    )
                )

    except PermissionError:
        pass

    return items


def get_file_extension_from_url_string(url):
    parsed_url = urlparse(url)

    return Path(parsed_url.path).suffix.lower()[1:]


def make_directory(directory_path: Path | str):
    Path(directory_path).mkdir(parents=True, exist_ok=True)


def read_from_file(file_path: Path | str) -> str:
    get_file_path_or_exception(file_path=file_path)

    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def remove_directory(directory_path: Path | str):
    Path(directory_path).rmdir()


def remove_file(file_path: Path | str):
    Path(file_path).unlink(missing_ok=True)


def write_to_file(file_path: Path | str, content: str):
    file_path = Path(file_path)

    make_directory(file_path.parent)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
