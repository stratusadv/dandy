from pathlib import Path

from dandy.conf import settings
from dandy.core.exceptions import DandyCriticalException


def get_file_path_or_exception(
        file_path: str | Path,
) -> Path:
    if Path(file_path).is_file():
        return Path(file_path)

    elif Path(settings.BASE_PATH, file_path).is_file():
        return Path(settings.BASE_PATH, file_path)

    else:
        message = f'File "{file_path}" does not exist'
        raise DandyCriticalException(message)
