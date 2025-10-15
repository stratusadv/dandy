from collections import UserDict

from typing import Self, Any

from dandy.core.exceptions import DandyCriticalException
from dandy.core.typing.registry import resolve_type_from_registry
from dandy.core.typing.typing import TypedKwargsDict


class TypedKwargs(UserDict):
    def __init__(
            self,
            data: TypedKwargsDict | dict[Any, Any],
    ):
        super().__init__(data)

    def __contains__(self, item: Self) -> bool:
        if not isinstance(item, TypedKwargs):
            message = f'Cannot compare TypedKwargs with {type(item)}. TypedKwargs can only be compared with TypedKwargs.'
            raise DandyCriticalException(message)

        if not self._is_valid_sub_set_typed_kwargs(item):
            return False

        for key in item:
            first_type = self[key][0]
            second_type = item[key][0]

            if isinstance(first_type, str):
                first_type = resolve_type_from_registry(
                    type_str=first_type
                )

            if isinstance(second_type, str):
                second_type = resolve_type_from_registry(
                    type_str=second_type
                )

            if first_type is not second_type:
                return False

        return True

    def _is_valid_sub_set_typed_kwargs(self, sub_typed_kwargs: Self) -> bool:
        return self.data.keys() >= sub_typed_kwargs.data.keys()
