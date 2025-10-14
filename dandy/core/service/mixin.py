from typing import ClassVar

from dandy.core.service.exceptions import ServiceCriticalException


class BaseServiceMixin:
    _required_attrs: ClassVar[tuple[str, ...]] = ()

    def __init_subclass__(cls):
        super().__init_subclass__()
        for attr in cls._required_attrs:
            if getattr(cls, attr) is None:
                message = f'"{cls.__name__}.{attr}" is not set'
                raise ServiceCriticalException(message)
