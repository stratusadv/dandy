import os
from enum import Enum
from typing import Type

from typing_extensions import List

from dandy.const import DEFAULT_SETTINGS_MODULE


def enum_to_list(enum_type: Type[Enum]) -> List:
    return [member.value for member in enum_type]


def get_settings_module_name() -> str:
    return os.getenv('DANDY_SETTINGS_MODULE') if os.getenv('DANDY_SETTINGS_MODULE') is not None else DEFAULT_SETTINGS_MODULE