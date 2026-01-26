
from pydantic import Field
from typing import Generic, TypeVar, Any

from dandy.intel.intel import BaseIntel, BaseListIntel

T = TypeVar('T')


class DecoderKeyIntel(BaseIntel, Generic[T]):
    key: T


class DecoderKeysIntel(BaseListIntel[T], Generic[T]):
    keys: list[T] = Field(default_factory=list)


class DecoderValuesIntel(BaseListIntel[Any]):
    values: list[Any] = Field(default_factory=list)
