from abc import ABC, abstractmethod
from typing import ClassVar, TypeVar

from dandy.core.service.exceptions import ServiceCriticalError

T = TypeVar('T')


class BaseServiceMixin(ABC):
    _required_attrs: ClassVar[tuple[str, ...]] = ()

    @abstractmethod
    def __init__(self, **kwargs) -> None:
        """Required for super() call chain"""

    def __init_subclass__(cls) -> None:
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

    @abstractmethod
    def reset(self) -> None:
        """Cannot use NotImplementedError do to call chain"""

