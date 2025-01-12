from enum import Enum
from typing import Type

from typing_extensions import List


def enum_to_list(enum_type: Type[Enum]) -> List:
    return [member.value for member in enum_type]