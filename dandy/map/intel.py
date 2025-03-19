from enum import Enum

from typing_extensions import Generic, TypeVar

from dandy.intel import BaseListIntel

T = TypeVar('T')


class MapSelectedValuesIntel(BaseListIntel[T], Generic[T]):
    pass