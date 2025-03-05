import json
from abc import ABC
from typing import Type

from pydantic import BaseModel
from pydantic.main import IncEx, create_model
from pydantic_core import from_json
from typing_extensions import Generator, Union, List, Generic, TypeVar, Self, Dict, get_origin, Tuple, Set, get_args

from dandy.intel.exceptions import IntelException
from dandy.intel.tools import get_field_annotation

T = TypeVar('T')

class BaseIntel(BaseModel, ABC):
    @classmethod
    def model_inc_ex_class_copy(
            cls,
            include: Union[IncEx, None] = None,
            exclude: Union[IncEx, None] = None,
    ) -> Type[Self]:
        if include is None and exclude is None:
            return cls
        
        fields = cls.model_fields

        if include and exclude:
            raise IntelException('include and exclude cannot be used together')
        
        def inc_ex_dict(inc_ex: IncEx) -> Dict[str, bool]:
            if inc_ex:
                return inc_ex if isinstance(inc_ex, dict) else {key: True for key in inc_ex}
            else:
                return {}

        include_dict = inc_ex_dict(include)
        exclude_dict = inc_ex_dict(exclude)

        process_fields = {}

        for field_name, field_info in fields.items():

            include_value = include_dict.get(field_name)
            exclude_value = exclude_dict.get(field_name)

            if isinstance(include_value, Dict) or isinstance(exclude_value, Dict):
                annotation = get_field_annotation(field_info)

                origin = get_origin(annotation)

                if origin in (list, List, tuple, Tuple, set, Set):
                    annotation = get_args(annotation)[0]

                if issubclass(annotation, BaseModel):
                    sub_model = annotation

                    new_sub_model = sub_model.model_inc_ex_class_copy(
                        include=include_value,
                        exclude=exclude_value,
                    )

                    process_fields[field_name] = (
                        new_sub_model if origin is None else origin[new_sub_model],
                        field_info.default_factory or field_info.default
                    )

                else:
                    process_fields[field_name] = (
                        annotation if origin is None else origin[annotation],
                        field_info.default_factory or field_info.default
                    )

            elif (include_value and exclude is None) or (exclude_value is None and include is None):
                process_fields[field_name] = (
                    field_info.annotation,
                    field_info.default_factory or field_info.default
                )

            elif exclude_value:
                pass

        return create_model(
            f'{cls.__name__}',
            **process_fields,
        )

    def model_validate_and_copy(self, update: dict) -> Self:
        return self.model_validate(self.model_copy(update=update))
        
    def model_validate_json_and_copy(self, update: str) -> Self:
        return self.model_validate_and_copy(update=from_json(update))
    

class BaseListIntel(BaseIntel, ABC, Generic[T]):
    items: List[T]

    def __getitem__(self, index) -> Union[List[T], T]:
        return self.items[index]

    def __iter__(self) -> Generator[T]:
        for item in self.items:
            yield item

    def __setitem__(self, index, value: T):
        self.items[index] = value

    def append(self, item: T):
        self.items.append(item)
