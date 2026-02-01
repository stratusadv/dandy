from abc import ABC
from typing import ClassVar, TypeVar

from dandy.core.service.exceptions import ServiceCriticalError

T = TypeVar('T')


class BaseServiceMixin(ABC):
    _required_attrs: ClassVar[tuple[str, ...]] = ()

    def __init_subclass__(cls):
        super().__init_subclass__()
        for attr in cls._required_attrs:
            if getattr(cls, attr) is None:
                message = f'"{cls.__name__}.{attr}" is not set'
                raise ServiceCriticalError(message)


    def _get_service_instance(self, service_class: type[T]) -> T:
        service_instance_attr = f'_{service_class.__name__}_instance'
        if getattr(self, service_instance_attr, None) is None:
            setattr(self, service_instance_attr, service_class(obj=self))

        return getattr(self, service_instance_attr)

    def reset_services(self):
        pass

