from functools import wraps

from dandy.constants import DEBUG_DEFAULT_NAME
from dandy.debug import DebugRecorder


def debug_recorder_to_html(debugger_name: str = DEBUG_DEFAULT_NAME):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                DebugRecorder.start_recording(debugger_name)

                return func(*args, **kwargs)

            finally:
                DebugRecorder.stop_recording(debugger_name)
                DebugRecorder.to_html_file(debugger_name)

        return wrapper

    return decorator
