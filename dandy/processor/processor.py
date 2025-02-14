from abc import abstractmethod, ABC

from typing_extensions import Any

from dandy.future.future import AsyncFuture
from dandy.processor.abc_meta import ProcessorABCMeta


class BaseProcessor(ABC, metaclass=ProcessorABCMeta):
    """
    Base class for all processing classes in dandy.
    """
    @classmethod
    @abstractmethod
    def process(cls, *args, **kwargs) -> Any:
        """
        This method has hooks on it to allow for easy debugging    
        :param args: Arguments 
        :param kwargs: Keyword Arguments
        :return: Any
        """
        ...

    @classmethod
    def process_to_future(cls, *args, **kwargs) -> AsyncFuture:
        """
        This method is used to generate an AsyncFuture of the process method
        :param args: Arguments
        :param kwargs: Keyword Arguments
        :return: AsyncFuture 
        """
        return AsyncFuture(cls.process, *args, **kwargs)
