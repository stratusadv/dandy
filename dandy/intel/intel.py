from __future__ import annotations

from abc import ABC
from types import UnionType
from typing import Any, Union

from pydantic import BaseModel, PrivateAttr
from pydantic.main import IncEx, create_model
from pydantic_core import from_json
from typing import Generic, TypeVar, Self, get_origin, Iterator

from dandy.intel.exceptions import IntelCriticalException
from dandy.intel.field.annotation import FieldAnnotation


class BaseIntel(BaseModel, ABC):
    @classmethod
    def _inc_ex_to_dict(cls, inc_ex: IncEx | None) -> dict:
        if inc_ex is not None:
            return inc_ex if isinstance(inc_ex, dict) else dict.fromkeys(inc_ex, True)

        return {}

    def model_to_kwargs(self) -> dict:
        return dict(self)

    @classmethod
    def model_inc_ex_class_copy(
        cls,
        include: IncEx | dict | None = None,
        exclude: IncEx | dict | None = None,
        intel_object: Self | None = None,
    ) -> type[BaseIntel]:
        if include is None and exclude is None:
            return create_model(cls.__name__, __base__=cls)

        if include and exclude:
            message = "include and exclude cannot be used together"
            raise IntelCriticalException(message)

        include_dict = cls._inc_ex_to_dict(include)
        exclude_dict = cls._inc_ex_to_dict(exclude)

        cls._validate_inc_ex_dict_or_error(
            include_dict,
            exclude_dict,
        )

        cls._validate_inc_ex_value_or_error(
            include,
            include_dict,
            exclude,
            exclude_dict,
            intel_object,
        )

        processed_fields = {}

        for field_name, field_info in cls.model_fields.items():
            include_value = include_dict.get(field_name)
            exclude_value = exclude_dict.get(field_name)

            field_annotation = FieldAnnotation(field_info.annotation, field_name)

            field_default_value = cls._get_field_default_value_from_field_info(field_info)

            field_annotation_type = False

            if isinstance(include_value, dict) or isinstance(exclude_value, dict):
                field_annotation_origin = field_annotation.origin

                if field_annotation_origin is UnionType:
                    field_annotation_origin = Union

                if issubclass(field_annotation.first_inner, BaseIntel):
                    sub_model: type[BaseIntel] = field_annotation.first_inner

                    new_sub_model = sub_model.model_inc_ex_class_copy(
                        include=include_value,
                        exclude=exclude_value,
                    )

                    field_annotation_type = (
                        new_sub_model
                        if field_annotation_origin is None
                        else field_annotation_origin[new_sub_model]
                    )

                else:
                    field_annotation_type = (
                        field_annotation.first_inner
                        if field_annotation_origin is None
                        else field_annotation_origin[field_annotation.first_inner]
                    )

            elif (include_value and exclude is None) or (
                exclude_value is None and include is None
            ):
                field_annotation_type = field_annotation.base

            if field_annotation_type:
                processed_fields[field_name] = (
                    field_annotation_type,
                    field_default_value,
                )

        return create_model(cls.__name__, **processed_fields, __base__=BaseIntel)

    @classmethod
    def model_json_inc_ex_schema(
        cls,
        include: IncEx | None = None,
        exclude: IncEx | None = None,
    ) -> dict:
        return cls.model_inc_ex_class_copy(
            include=include,
            exclude=exclude,
        ).model_json_schema()

    def model_object_json_inc_ex_schema(
        self, include: IncEx | None = None, exclude: IncEx | None = None
    ) -> dict:
        return self.model_inc_ex_class_copy(
            include=include, exclude=exclude, intel_object=self
        ).model_json_schema()

    def model_validate_and_copy(self, update: dict) -> Self:
        return self.model_validate(
            obj=self.model_copy(update=update).model_dump(warnings=False),
        )

    def model_validate_json_and_copy(self, json_data: str) -> Self:
        return self.model_validate_and_copy(update=from_json(json_data))

    @classmethod
    def _get_field_default_value_from_field_info(
        cls,
        field_info: Any,
    ) -> Any:
        field_default_value = field_info.default_factory or field_info.default

        if isinstance(field_default_value, type):
            field_default_value = field_default_value()

        return field_default_value

    @classmethod
    def _validate_inc_ex_dict_or_error(
        cls,
        include_dict: dict,
        exclude_dict: dict,
    ):
        field_names = set(cls.model_fields.keys())

        if include_dict:
            include_field_names = set(include_dict.keys())

            if not include_field_names.issubset(field_names):
                message = f"include failed on {cls.__name__} because it does not have the following fields: {field_names.difference(include_field_names)}."
                raise IntelCriticalException(message)

        if exclude_dict:
            exclude_field_names = set(exclude_dict.keys())

            if not exclude_field_names.issubset(field_names):
                message = f"exclude failed on {cls.__name__} because it does not have the following fields: {field_names.difference(exclude_field_names)}."
                raise IntelCriticalException(message)

    @classmethod
    def _validate_inc_ex_value_or_error(
        cls,
        include: IncEx | dict | None,
        include_dict: dict,
        exclude: IncEx | dict | None,
        exclude_dict: dict,
        intel_object: Self | None,
    ):
        for field_name, field_info in cls.model_fields.items():
            include_value = include_dict.get(field_name)
            exclude_value = exclude_dict.get(field_name)

            if not isinstance(include_value, dict) and not isinstance(
                exclude_value, dict
            ):
                if include is None and exclude_value and field_info.is_required():
                    if intel_object is None:
                        message = f"{field_name} is required and cannot be excluded"
                        raise IntelCriticalException(message)

                    if getattr(intel_object, field_name) is None:
                        message = f"{field_name} is required and has no value therefore cannot be excluded"
                        raise IntelCriticalException(message)

                if (
                    exclude is None
                    and include_value is None
                    and field_info.is_required()
                ):
                    if intel_object is None:
                        message = f"{field_name} is required and must be included"
                        raise IntelCriticalException(message)

                    if getattr(intel_object, field_name) is None:
                        message = f"{field_name} is required and has no value therefore it must be included"
                        raise IntelCriticalException(message)


T = TypeVar("T")


class BaseListIntel(BaseIntel, ABC, Generic[T]):
    _list_name: str = PrivateAttr(default=None)

    def model_post_init(self, __context: Any, /):
        list_fields = [
            name
            for name, field in self.__class__.model_fields.items()
            if get_origin(field.annotation) is list
        ]

        if len(list_fields) != 1:
            message = "BaseListIntel sub classes can only have exactly one list field attribute and must be declared with typing"
            raise ValueError(message)

        self._list_name = list_fields[0]

    def __getitem__(self, index: int) -> list[T] | T:
        return getattr(self, self._list_name)[index]

    def __iter__(self) -> Iterator[T]:
        yield from getattr(self, self._list_name)

    def __len__(self) -> int:
        return len(getattr(self, self._list_name))

    def __setitem__(self, index: int, value: T):
        getattr(self, self._list_name)[index] = value

    def append(self, item: T):
        getattr(self, self._list_name).append(item)

    def extend(self, items: list[T]):
        getattr(self, self._list_name).extend(items)


class DefaultIntel(BaseIntel):
    text: str
