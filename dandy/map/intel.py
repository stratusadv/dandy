from enum import Enum
from typing import List

from pydantic import Field
from typing_extensions import Generic, TypeVar, Self

from dandy.intel import BaseListIntel

T = TypeVar('T')


class MapValuesIntel(BaseListIntel[T], Generic[T]):
    items: List[T] = Field(default_factory=list)
