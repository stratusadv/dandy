from typing import List

from pydantic import Field
from typing_extensions import Generic, TypeVar

from dandy.intel import BaseIntel, BaseListIntel

T = TypeVar('T')


class MapKeyIntel(BaseIntel, Generic[T]):
    key: T


class MapKeysIntel(BaseListIntel, Generic[T]):
    keys: List[T] = Field(default_factory=list)
