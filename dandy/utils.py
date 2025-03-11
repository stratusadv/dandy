import os
import re
from enum import Enum

from typing_extensions import List, Type

from dandy.constants import DEFAULT_SETTINGS_MODULE


def pascal_to_title_case(pascal_case_string: str) -> str:
    return ' '.join(re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', pascal_case_string))


def enum_to_list(enum_type: Type[Enum]) -> List:
    return [member.value for member in enum_type]


def get_settings_module_name() -> str:
    return os.getenv('DANDY_SETTINGS_MODULE') if os.getenv('DANDY_SETTINGS_MODULE') is not None else DEFAULT_SETTINGS_MODULE