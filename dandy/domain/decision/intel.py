from typing import Any, Generic, TypeVar

from pydantic import Field

from dandy.domain.intel.intel import BaseIntel, BaseListIntel

T = TypeVar('T')


class DecisionChoiceIntel(BaseIntel, Generic[T]):
    key: T


class DecisionChoicesIntel(BaseListIntel[list[T]], Generic[T]):
    keys: list[T] = Field(default_factory=list)


class DecisionValuesIntel(BaseListIntel[Any]):
    values: list[Any] = Field(default_factory=list)
