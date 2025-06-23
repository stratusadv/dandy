from collections import UserDict

from typing_extensions import Self

from dandy.core.exceptions import DandyCriticalException
from dandy.core.typing.registry import resolve_type_from_registry
from dandy.core.typing.typing import TypedKwargsDict


class TypedKwargs(UserDict):
    def __init__(
            self,
            data: TypedKwargsDict,
            metadata = None
    ):
        super().__init__(data)
        self.metadata = metadata

    def __contains__(self, item: Self) -> bool:
        if not isinstance(item, TypedKwargs):
            raise DandyCriticalException(
                f'Cannot compare TypedKwargs with {type(item)}. TypedKwargs can only be compared with TypedKwargs.'
            )

        # THIS IS ALL FUCKED UP RIGHT NOW

        0 / 0

        if not self.keys() >= item.keys():
            return False

        for key, value in item.items():
            if isinstance(self[key][0], str):
                first_type = resolve_type_from_registry(self[key][0])
            else:
                first_type = self[key][0]

            if isinstance(item[key][0], str):
                second_type = resolve_type_from_registry(item[key][0])
            else:
                second_type = item[key][0]

            if not isinstance(first_type, second_type):
                return False

        return True