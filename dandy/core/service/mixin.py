from abc import abstractmethod, ABC
from typing import ClassVar, TypeVar, Any, Self

from dandy.core.service.exceptions import ServiceCriticalError
from dandy.core.service.service import BaseService

T = TypeVar('T')


class BaseServiceMixin(ABC):
    _required_attrs: ClassVar[tuple[str, ...]] = ()
    _service_instance: BaseService = ...

    def __init_subclass__(cls):
        super().__init_subclass__()
        for attr in cls._required_attrs:
            if getattr(cls, attr) is None:
                message = f'"{cls.__name__}.{attr}" is not set'
                raise ServiceCriticalError(message)

    def _get_service_instance(self, service_class: type[T]) -> T:
        if self._service_instance is ...:
            self._service_instance = service_class(
                obj=self
            )

        return self._service_instance

    @abstractmethod
    def reset_services(self):
        raise NotImplementedError
