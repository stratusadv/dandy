from typing import List

from pydantic import Field
from typing import Generic, TypeVar, Any

from dandy.intel.intel import BaseIntel, BaseListIntel

T = TypeVar('T')


class MapKeyIntel(BaseIntel, Generic[T]):
    key: T


class MapKeysIntel(BaseListIntel[T], Generic[T]):
    keys: list[T] = Field(default_factory=list)


class MapValuesIntel(BaseListIntel[Any]):
    values: list[Any] = Field(default_factory=list)