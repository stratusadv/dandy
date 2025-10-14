from functools import wraps
from pathlib import Path

from typing import Callable

from dandy.recorder import Recorder
from dandy.recorder.recorder import DEFAULT_RECORDER_OUTPUT_PATH


def _recorder_to_file_decorator_function(
        func: Callable,
        args: tuple,
        kwargs: dict,
        recording_name: str | None,
        renderer: str,
        path: Path | str,
):
    if recording_name is None:
        recording_name = (
            str(func.__qualname__)
            .replace('.', '_')
            .replace('<', '')
            .replace('>', '')
            .lower()
        )

    try:
        Recorder.start_recording(recording_name)

        return func(*args, **kwargs)

    finally:
        Recorder.stop_recording(recording_name)
        Recorder.to_file(recording_name, renderer, path)
        Recorder.delete_recording(recording_name)


def recorder_to_html_file(recording_name: str | None = None, path: Path | str = DEFAULT_RECORDER_OUTPUT_PATH):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return _recorder_to_file_decorator_function(func, args, kwargs, recording_name, 'html', path)

        return wrapper

    return decorator


def recorder_to_json_file(recording_name: str | None = None, path: Path | str = DEFAULT_RECORDER_OUTPUT_PATH):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return _recorder_to_file_decorator_function(func, args, kwargs, recording_name, 'json', path)

        return wrapper

    return decorator


def recorder_to_markdown_file(recording_name: str | None = None, path: Path | str = DEFAULT_RECORDER_OUTPUT_PATH):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return _recorder_to_file_decorator_function(func, args, kwargs, recording_name, 'markdown', path)

        return wrapper

    return decorator
