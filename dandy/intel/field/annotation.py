from types import NoneType

from typing import get_origin, get_args, Type, List, Tuple, Set, Any

from dandy.intel.exceptions import IntelCriticalException


class FieldAnnotation:
    def __init__(self, annotation: Type | None, field_name: str):
        self.annotation = annotation

        if self.first_inner_origin_is_iterable:
            self.annotation = self.first_inner

        self.field_name = field_name

    @property
    def args(self) -> tuple:
        return get_args(self.annotation)

    @property
    def base(self) -> Any:
        return self.annotation

    @property
    def first_inner(self) -> Any:
        inner = [arg for arg in self.args if arg is not None and arg is not NoneType]

        if len(inner) == 1:
            return inner[0]

        if len(inner) > 1:
            message = (
                f'Failed to get annotation on field "{self.field_name}" because a "{self.origin}" had more than one '
                f'non-None type or this field\'s annotation was beyond the complexity of 2 annotation origins.'
            )
            raise IntelCriticalException(message)

        return self.annotation

    @property
    def first_inner_origin_is_iterable(self) -> bool:
        return get_origin(self.first_inner) in (list, List, tuple, Tuple, set, Set)

    @property
    def origin(self) -> Type | None:
        return get_origin(self.annotation)
