from enum import Enum
from typing import List

from typing_extensions import Generic, TypeVar, Self

from dandy.intel import BaseListIntel

T = TypeVar('T')


class MapSelectedValuesIntel(BaseListIntel[T], Generic[T]):
    pass
