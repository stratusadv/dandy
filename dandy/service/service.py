from __future__ import annotations

from abc import ABC
from typing import Any, Generic, TypeVar

from dandy.service.exceptions import ServiceCriticalException

TypeAny = TypeVar('TypeAny', bound=Any, covariant=True)


class BaseService(ABC, Generic[TypeAny]):
    def __init__(self, obj: Any = None):
        self._obj_type_name: str = str(
            list(self.__class__.__annotations__.values())[0]
        ).split('.')[-1]

        if obj is None:
            return

        self._obj_mro_type_names = [cls.__name__ for cls in obj.__class__.__mro__]

        if not self._obj_type_name in self._obj_mro_type_names:
            raise ServiceCriticalException(
                f'{self.__class__.__name__} was instantiated with obj type "{obj.__class__.__name__}" and failed as it was expecting "{self._obj_type_name}".'
            )

        self._obj_type: type[TypeAny] = obj.__class__

        if self._obj_type is None or self._obj_type is ...:
            raise ServiceCriticalException(
                f'{self.__class__.__name__} top class attribute must have an annotated type.')

        self.obj: TypeAny = obj

        if ABC not in self.__class__.__bases__:
            if not self._obj_is_valid:
                raise ServiceCriticalException(f'{self._obj_type_name} failed to validate on {self.__class__.__name__}')

        self.__post_init__()

    def __init_subclass__(cls):
        super().__init_subclass__()

        if ABC not in cls.__bases__:
            if 'obj' not in cls.__annotations__:
                raise ServiceCriticalException(
                    f'{cls.__name__} must have an "obj" attribute annotated with a type.')

            # Typing Does not work properly for services if you override __get__ in the BaseService class.
            # This is a workaround and should be fixed in future versions of the python lsp.
            def __get__(self, instance, owner):

                if instance is None:
                    target: BaseService | Any = owner()
                else:
                    target: BaseService | Any = instance

                if issubclass(target.__class__, BaseService):

                    self._validate_base_service_target_or_error(target)

                    return cls(getattr(target, 'obj'))

                return cls(target)

            setattr(cls, '__get__', __get__)

    def __post_init__(self):
        pass

    @property
    def obj_class(self) -> type[TypeAny]:
        return self._obj_type

    @property
    def _obj_is_valid(self) -> bool:
        return isinstance(self.obj, self._obj_type)

    def _validate_base_service_target_or_error(self, target: BaseService):
        if self._obj_type_name not in target._obj_mro_type_names:
            raise ServiceCriticalException(
                f'{target.__class__.__name__} must use the same obj type as {self.__class__.__name__}. {self._obj_type_name} is not in {target._obj_mro_type_names}')


