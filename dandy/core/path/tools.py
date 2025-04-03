from pathlib import Path
from typing import Union, List

from dandy.conf import settings
from dandy.core.exceptions import DandyCriticalException


def get_file_path_or_exception(
        file_path: Union[str, Path, List[str]],
        relative_parents: int = 0,
) -> Path:
    if relative_parents > 0:
        original_caller_path = get_original_caller_relative_path()

        file_path = Path(
            Path(original_caller_path).resolve().parents[relative_parents - 1],
            file_path,
        )

    if Path(file_path).is_file():
        return Path(file_path)

    elif Path(settings.BASE_PATH, file_path).is_file():
        return Path(settings.BASE_PATH, file_path)

    elif Path(get_original_caller_relative_path().parent.resolve(), file_path).is_file():
        return Path(get_original_caller_relative_path().parent.resolve(), file_path)

    else:
        raise DandyCriticalException(f'File "{file_path}" does not exist')


def get_original_caller_relative_path() -> Path | None:
    import inspect

    stack = inspect.stack()

    for frame_info in reversed(stack):
        if not any(module in frame_info.filename for module in ['unittest', 'pytest']):
            return Path(frame_info.filename)

    return None

