import json
from abc import abstractmethod, ABCMeta

from dandy.core.utils import json_default
from dandy.debug.debug import DebugRecorder
from dandy.debug.events import RunEvent, ResultEvent
from dandy.future.future import AsyncFuture


class ProcessDebugABCMeta(ABCMeta):
    def __new__(cls, name, bases, dct):
        if 'process' in dct:
            original_process = dct['process']

            if isinstance(original_process, classmethod):
                original_func = original_process.__func__

                def wrapped_process(cls, *args, **kwargs):
                    if DebugRecorder.is_recording and not getattr(cls, "_debugger_called", False):
                        DebugRecorder.add_event(
                            RunEvent(
                                actor=cls.__name__,
                                action='Process',
                                description=json.dumps(
                                    {
                                        'args': args,
                                        'kwargs': kwargs
                                    },
                                    indent=4,
                                    default=json_default
                                )
                            )
                        )
                        cls._debugger_called = True

                    result = original_func(cls, *args, **kwargs)

                    if DebugRecorder.is_recording and not getattr(cls, "_debugger_called", False):
                        DebugRecorder.add_event(
                            ResultEvent(
                                actor=cls.__name__,
                                action='Process Returned Result',
                                description=json.dumps(
                                    {
                                        'returned result': result
                                    },
                                    indent=4,
                                    default=json_default
                                )
                            )
                        )

                    cls._debugger_called = False

                    return result

                dct['process'] = classmethod(wrapped_process)

        return super().__new__(cls, name, bases, dct)


class Handler(metaclass=ProcessDebugABCMeta):
    @classmethod
    @abstractmethod
    def process(cls, **kwargs):
        ...

    @classmethod
    def process_to_future(cls, *args, **kwargs) -> AsyncFuture:
        return AsyncFuture(cls.process, *args, **kwargs)