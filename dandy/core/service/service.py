from __future__ import annotations

from abc import ABC
from typing import Any, Generic, TypeVar

from dandy.core.service.exceptions import ServiceCriticalException

TypeAny = TypeVar('TypeAny', bound=Any, covariant=True)


class BaseService(ABC, Generic[TypeAny]):
    def __new__(cls, obj: Any = None) -> Any:
        service_instance = cls.get_obj_service_instance(obj)

        if service_instance is not None:
            return service_instance
        else:
            return super().__new__(cls)

    def __init__(self, obj: Any = None):
        if self.has_obj_service_instance(obj):
            return

        self._obj_type_name: str = str(
            list(self.__class__.__annotations__.values())[0]
        ).split('.')[-1]

        if obj is None:
            return

        self._obj_mro_type_names = [cls.__name__ for cls in obj.__class__.__mro__]

        if not self._obj_type_name in self._obj_mro_type_names:
            message = f'{self.__class__.__name__} was instantiated with obj type "{obj.__class__.__name__}" and failed as it was expecting "{self._obj_type_name}".'
            raise ServiceCriticalException(message)

        self._obj_type: type[TypeAny] = obj.__class__

        if self._obj_type is None or self._obj_type is ...:
            message = f'{self.__class__.__name__} top class attribute must have an annotated type.'
            raise ServiceCriticalException(message)

        self.obj: TypeAny = obj

        if ABC not in self.__class__.__bases__:
            if not self._obj_is_valid:
                message = f'{self._obj_type_name} failed to validate on {self.__class__.__name__}'
                raise ServiceCriticalException(message)

        self.__post_init__()

        if not hasattr(obj, self.generate_service_instance_name(self.__class__)):
            message = f'To use "{self.__class__.__name__}" can only be attached to an object with a "{self.generate_service_instance_name(self.__class__)}" attribute.'
            raise ServiceCriticalException(message)

        self.set_obj_service_instance(obj, self)

    def __init_subclass__(cls):
        super().__init_subclass__()

        if ABC not in cls.__bases__:
            if 'obj' not in cls.__annotations__:
                message = f'{cls.__name__} must have an "obj" attribute annotated with a type.'
                raise ServiceCriticalException(message)

            # Typing Does not work properly for services if you override __get__ in the BaseService class.
            # This is a workaround and should be fixed in future versions of the python lsp.
            def __get__(self, instance, owner):

                if instance is None:
                    target: cls | Any = owner()
                else:
                    target: cls | Any = instance

                if issubclass(target.__class__, BaseService):
                    self._validate_base_service_target_or_error(target)

                    return cls(getattr(target, 'obj'))

                return cls(target)

            setattr(cls, '__get__', __get__)

    def __post_init__(self):
        pass

    @staticmethod
    def generate_service_instance_name(cls) -> str:
        return f'_{cls.__name__}_instance'

    @classmethod
    def get_obj_service_instance(cls, obj: Any) -> Any | None:
        return getattr(
            obj,
            cls.generate_service_instance_name(cls),
            None
        )

    def has_obj_service_instance(self, obj: Any) -> bool:
        return self.get_obj_service_instance(obj) is not None

    @classmethod
    def set_obj_service_instance(cls, obj: Any, service_instance: BaseService):
        setattr(
            obj,
            cls.generate_service_instance_name(cls),
            service_instance
        )

    @property
    def obj_class(self) -> type[TypeAny]:
        return self._obj_type

    @property
    def _obj_is_valid(self) -> bool:
        return isinstance(self.obj, self._obj_type)

    def _validate_base_service_target_or_error(self, target: BaseService):
        if self._obj_type_name not in target._obj_mro_type_names:
            message = f'{target.__class__.__name__} must use the same obj type as {self.__class__.__name__}. {self._obj_type_name} is not in {target._obj_mro_type_names}'
            raise ServiceCriticalException(message)
