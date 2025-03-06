from abc import ABC
from typing import Type

from pydantic import BaseModel
from pydantic.main import IncEx, create_model
from pydantic_core import from_json
from typing_extensions import Generator, Union, List, Generic, TypeVar, Self, Dict

from dandy.intel.field.annotation import FieldAnnotation
from dandy.intel.exceptions import IntelException


T = TypeVar('T')


class BaseIntel(BaseModel, ABC):
    @classmethod
    def model_inc_ex_class_copy(
            cls,
            include: Union[IncEx, None] = None,
            exclude: Union[IncEx, None] = None,
    ) -> Type[Self]:
        if include is None and exclude is None:
            return create_model(
                cls.__name__, 
                __base__=cls
            )
        
        if include and exclude:
            raise IntelException('include and exclude cannot be used together')
        
        def inc_ex_dict(inc_ex: IncEx) -> Dict[str, bool]:
            if inc_ex:
                return inc_ex if isinstance(inc_ex, dict) else {key: True for key in inc_ex}
            else:
                return {}

        include_dict = inc_ex_dict(include)
        exclude_dict = inc_ex_dict(exclude)

        processed_fields = {}
        
        for field_name, field_info in cls.model_fields.items():

            include_value = include_dict.get(field_name)
            exclude_value = exclude_dict.get(field_name)

            # TODO: Handle required fields            
            # if (include is None and exclude_value and field_info.is_required) or (exclude is None and include_value is None and field_info.is_required):
            #     raise IntelException(f"{field_name} is required and cannot be excluded or not included")

            field_annotation = FieldAnnotation(field_info)
            field_factory = field_info.default_factory or field_info.default

            if isinstance(include_value, Dict) or isinstance(exclude_value, Dict):

                if issubclass(field_annotation.first_inner, BaseIntel):
                    sub_model = field_annotation.first_inner

                    new_sub_model = sub_model.model_inc_ex_class_copy(
                        include=include_value,
                        exclude=exclude_value,
                    )

                    processed_fields[field_name] = (
                        new_sub_model if field_annotation.origin is None else field_annotation.origin[new_sub_model],
                        field_factory,
                    )
                    
                else:
                    processed_fields[field_name] = (
                        field_annotation.first_inner if field_annotation.origin is None else field_annotation.origin[field_annotation.first_inner],
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
