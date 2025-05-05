from enum import Enum
from typing import List, Any

from pydantic import Field
from typing_extensions import Generic, TypeVar, Self

from dandy.intel import BaseListIntel, BaseIntel

T = TypeVar('T')


class MapValueIntel(BaseIntel, Generic[T]):
    item: T


class MapValuesIntel(BaseListIntel[T], Generic[T]):
    items: List[T] = Field(default_factory=list)
