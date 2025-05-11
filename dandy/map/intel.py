from typing import List

from pydantic import Field
from typing_extensions import Generic, TypeVar, Any

from dandy.intel import BaseIntel, BaseListIntel

T = TypeVar('T')


class MapKeyIntel(BaseIntel, Generic[T]):
    key: T


class MapKeysIntel(BaseListIntel[T], Generic[T]):
    keys: T = Field(default_factory=list)


class MapValuesIntel(BaseListIntel[Any]):
    values: List[Any] = Field(default_factory=list)