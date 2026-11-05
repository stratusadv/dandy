import random
import re
import string
from typing import Any, Iterable

from pydantic import ValidationError

# Cap in characters for external output fed back into the model's
# conversation: command output, tool results, and large file, search, and
# listing results are all limited to this length so one oversized result can
# never blow past the context window.
OUTPUT_CHARACTER_LIMIT = 8000


def pascal_to_title_case(pascal_case_string: str) -> str:
    return ' '.join(re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', pascal_case_string)).title()


def generate_recorder_event_id() -> str:
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(random.choices(alphabet, k=4))


def generate_forwardable_kwargs_if_not_none(**kwargs) -> dict:
    return {key: value for key, value in kwargs.items() if value is not None}


def pydantic_validation_error_to_str(error: ValidationError) -> str:
    return error.__str__()


def python_obj_to_markdown(python_obj: Any, markdown_str: str = '', level: int = 2) -> str:

    if isinstance(python_obj, dict):
        for key, value in python_obj.items():
            if level <= 6:
                markdown_str += f'{"#" * level} {key}\n\n'
            else:
                markdown_str += f'**{key}**\n\n'

            if isinstance(value, dict):
                markdown_str = python_obj_to_markdown(value, markdown_str, level + 1)

            elif isinstance(value, list):
                for item in value:
                    markdown_str = python_obj_to_markdown(item, markdown_str, level + 1)

            else:
                markdown_str += f'{value}\n\n'

    elif isinstance(python_obj, Iterable) and not isinstance(python_obj, str):
        for item in python_obj:
            markdown_str = python_obj_to_markdown(item, markdown_str, level)

    else:
        markdown_str += f'{python_obj}\n\n'

    return markdown_str


def truncate_output(
    text: str, limit: int = OUTPUT_CHARACTER_LIMIT, marker: str = '\n... (truncated)'
) -> str:
    """Cap `text` at `limit` characters without splitting a line mid-way.

    When the text is longer than `limit`, it is cut to `limit` characters and
    trimmed back to the start of the last complete line (when a newline falls
    before the cut), then `marker` is appended. Text that already fits is
    returned unchanged.
    """
    if len(text) <= limit:
        return text

    kept = text[:limit]

    newline_position = kept.rfind('\n')

    if newline_position > 0:
        kept = kept[:newline_position]

    return kept + marker
