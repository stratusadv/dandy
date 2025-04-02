import base64
import os
import re
from enum import Enum
from pathlib import Path
from typing import Type, List, Any, Iterable

from pydantic import ValidationError
from typing_extensions import Union

from dandy.constants import DEFAULT_SETTINGS_MODULE
from dandy.core.exceptions import DandyCriticalException
from dandy.intel import BaseIntel


def encode_file_to_base64(file_path: Union[str, Path]) -> str:
    if not Path(file_path).is_file():
        raise DandyCriticalException(f'File "{file_path}" does not exist')

    with open(file_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


def enum_to_list(enum_type: Type[Enum]) -> List:
    return [member.value for member in enum_type]


def get_settings_module_name() -> str:
    return os.getenv('DANDY_SETTINGS_MODULE') if os.getenv(
        'DANDY_SETTINGS_MODULE') is not None else DEFAULT_SETTINGS_MODULE


def json_default(obj):
    if isinstance(obj, BaseIntel):
        return obj.model_dump()
    else:
        try:
            return str(obj)
        except TypeError:
            return '<unserializable value>'


def pascal_to_title_case(pascal_case_string: str) -> str:
    return ' '.join(re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', pascal_case_string))


def pydantic_validation_error_to_str(error: ValidationError) -> str:
    return error.__str__()


def python_obj_to_markdown(
        python_obj: Any,
        markdown_str: str = '',
        level: int = 2
) -> str:

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

    elif isinstance(python_obj, Iterable):
        for item in python_obj:
            markdown_str = python_obj_to_markdown(item, markdown_str, level)

    else:
        markdown_str += f'{python_obj}\n\n'

    return markdown_str
