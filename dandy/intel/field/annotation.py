from types import UnionType, NoneType

from pydantic.fields import FieldInfo
from typing_extensions import get_origin, Union, get_args, Type, List, Tuple, Set

from dandy.intel.exceptions import IntelException


class FieldAnnotation:
    def __init__(self, field_info: FieldInfo):
        self.field_info = field_info

    @property
    def args(self) -> tuple:
        return get_args(self.field_info.annotation)

    @property
    def base(self):
        return self.field_info.annotation

    @property
    def first_inner(self):
        inner = [arg for arg in self.args if arg is not None and arg is not NoneType]

        if len(inner) == 1:
            return inner[0]
        elif len(inner) > 1:
            raise IntelException(
                f"Failed to get annotation on field '{self.field_info.title}' because a {self.origin} had more than one non-None Type, had: {self.args}")

        return self.field_info.annotation

    @property
    def origin(self) -> Type:
        return get_origin(self.field_info.annotation)

    @property
    def origin_is_iterable(self) -> bool:
        return self.origin in (list, List, tuple, Tuple, set, Set)

