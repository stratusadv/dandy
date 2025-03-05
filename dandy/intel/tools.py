from types import UnionType, NoneType

from pydantic.fields import FieldInfo
from typing_extensions import Type, get_origin, get_args, Union

from dandy.intel.exceptions import IntelException


def get_field_annotation(field_info: FieldInfo) -> Type:
    annotation_origin = get_origin(field_info.annotation)

    if annotation_origin is Union or annotation_origin is UnionType:
        annotation_args = get_args(field_info.annotation)
        inner_annotations = [arg for arg in annotation_args if arg is not None and arg is not NoneType]

        if len(inner_annotations) == 1:
            return inner_annotations[0]
        else:
            raise IntelException(
                f"Intel include failed on field '{field_info.title}' because a Union had more than one non-None, had annotations: {annotation_args}")

    else:
        return field_info.annotation

