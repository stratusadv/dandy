import logging
from functools import wraps

from dandy.debug import DebugRecorder
from tests.llm.constants import TESTING_LLM_CONFIGS


def debug_recorder_to_html(debug_name: str = 'default'):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                DebugRecorder.start_recording(debug_name)

                return func(*args, **kwargs)

            finally:
                DebugRecorder.stop_recording(debug_name)
                DebugRecorder.to_html_file(debug_name)

        return wrapper

    return decorator
