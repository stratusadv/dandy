from functools import wraps

from dandy.constants import RECORDING_DEFAULT_NAME
from dandy.recorder import Recorder


def recorder_to_html(recording_name: str = RECORDING_DEFAULT_NAME):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                Recorder.start_recording(recording_name)

                return func(*args, **kwargs)

            finally:
                Recorder.stop_recording(recording_name)
                Recorder.to_file(
                    'html',
                    recording_name,
                )

        return wrapper

    return decorator
