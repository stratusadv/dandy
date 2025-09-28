from __future__ import annotations

from abc import ABC
from typing import Type, Any

from pydantic import BaseModel, Field, PrivateAttr
from pydantic.main import IncEx, create_model
from pydantic_core import from_json
from typing import Generator, List, Generic, TypeVar, Self, Dict, get_origin

from dandy.intel.exceptions import IntelCriticalException
from dandy.intel.field.annotation import FieldAnnotation

T = TypeVar('T')


class BaseIntel(BaseModel, ABC):
    @classmethod
    def check_inc_ex(
            cls,
            include_dict: Dict,
            exclude_dict: Dict,
    ):

        field_names = set(cls.model_fields.keys())

        if include_dict:
            include_field_names = set(include_dict.keys())

            if not include_field_names.issubset(field_names):
                message = f'include failed on {cls.__name__} because it does not have the following fields: {field_names.difference(include_field_names)}.'
                raise IntelCriticalException(message)

        if exclude_dict:
            exclude_field_names = set(exclude_dict.keys())

            if not exclude_field_names.issubset(field_names):
                message = f'exclude failed on {cls.__name__} because it does not have the following fields: {field_names.difference(exclude_field_names)}.'
                raise IntelCriticalException(message)

    def model_to_kwargs(self) -> dict:
        return dict(self)

    @classmethod
    def model_inc_ex_class_copy(
            cls,
            include: IncEx | Dict | None = None,
            exclude: IncEx | Dict | None = None,
            intel_object: Self | None = None
    ) -> Type[BaseIntel]:
        if include is None and exclude is None:
            return create_model(
                cls.__name__,
                __base__=cls
            )

        if include and exclude:
            message = 'include and exclude cannot be used together'
            raise IntelCriticalException(message)

        def inc_ex_dict(inc_ex: IncEx | None) -> Dict:
            if inc_ex is not None:
                return inc_ex if isinstance(inc_ex, dict) else {key: True for key in inc_ex}
            else:
                return {}

        include_dict = inc_ex_dict(include)
        exclude_dict = inc_ex_dict(exclude)

        cls.check_inc_ex(include_dict, exclude_dict)

        processed_fields = {}

        for field_name, field_info in cls.model_fields.items():

            include_value = include_dict.get(field_name)
            exclude_value = exclude_dict.get(field_name)

            if not isinstance(include_value, Dict) and not isinstance(exclude_value, Dict):
                if include is None and exclude_value and field_info.is_required():
                    if intel_object is None:
                        message = f'{field_name} is required and cannot be excluded'
                        raise IntelCriticalException(message)

                    elif getattr(intel_object, field_name) is None:
                        message = f'{field_name} is required and has no value therefore cannot be excluded'
                        raise IntelCriticalException(message)

                if exclude is None and include_value is None and field_info.is_required():
                    if intel_object is None:
                        message = f'{field_name} is required and must be included'
                        raise IntelCriticalException(message)

                    elif getattr(intel_object, field_name) is None:
                        message = f"{field_name} is required and has no value therefore it must be included"
                        raise IntelCriticalException(message)

            field_annotation = FieldAnnotation(field_info.annotation, field_name)

            # Todo: this is creating the warning when running test on the Agent (Debug)
            field_factory = field_info.default_factory or field_info.default

            if isinstance(include_value, Dict) or isinstance(exclude_value, Dict):

                if issubclass(field_annotation.first_inner, BaseIntel):
                    sub_model: Type[BaseIntel] = field_annotation.first_inner

                    new_sub_model = sub_model.model_inc_ex_class_copy(
                        include=include_value,
                        exclude=exclude_value,
                    )

                    processed_fields[field_name] = (
                        new_sub_model if field_annotation.origin is None else field_annotation.origin[
                            new_sub_model
                        ],
                        field_factory,
                    )

                else:
                    processed_fields[field_name] = (
                        field_annotation.first_inner if field_annotation.origin is None else field_annotation.origin[
                            field_annotation.first_inner
                        ],
                        field_factory,
                    )

            elif (include_value and exclude is None) or (exclude_value is None and include is None):
                processed_fields[field_name] = (
                    field_annotation.base,
                    field_factory,
                )

        return create_model(
            cls.__name__,
            **processed_fields,
            __base__=BaseIntel
        )

    @classmethod
    def model_json_inc_ex_schema(
            cls,
            include: IncEx | None = None,
            exclude: IncEx | None = None,
    ) -> Dict:
        return cls.model_inc_ex_class_copy(
            include=include,
            exclude=exclude,
        ).model_json_schema()

    def model_object_json_inc_ex_schema(
            self,
            include: IncEx | None = None,
            exclude: IncEx | None = None
    ) -> Dict:
        return self.model_inc_ex_class_copy(
            include=include,
            exclude=exclude,
            intel_object=self
        ).model_json_schema()

    def model_validate_and_copy(self, update: dict) -> Self:
        return self.model_validate(
            obj=self.model_copy(update=update).model_dump(
                warnings=False
            ),
        )

    def model_validate_json_and_copy(self, json_data: str) -> Self:
        return self.model_validate_and_copy(update=from_json(json_data))


class BaseListIntel(BaseIntel, ABC, Generic[T]):
    _list_name: str = PrivateAttr(default=None)

    def model_post_init(self, __context: Any):
        list_fields = [
            name for name, field in self.__class__.model_fields.items()
            if get_origin(field.annotation) is list
        ]

        if len(list_fields) != 1:
            message = f'BaseListIntel sub classes can only have exactly one list field attribute and must be declared with typing'
            raise ValueError(message)

        self._list_name = list_fields[0]

    def __getitem__(self, index) -> List[T] | T:
        return getattr(self, self._list_name)[index]

    def __iter__(self) -> Generator[T, None, None]:
        yield from getattr(self, self._list_name)

    def __len__(self) -> int:
        return len(getattr(self, self._list_name))

    def __setitem__(self, index, value: T):
        getattr(self, self._list_name)[index] = value

    def append(self, item: T):
        getattr(self, self._list_name).append(item)

    def extend(self, items: List[T]):
        getattr(self, self._list_name).extend(items)


class DefaultIntel(BaseIntel):
    content: str
