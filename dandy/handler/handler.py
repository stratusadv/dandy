from abc import abstractmethod, ABC, ABCMeta
from typing import Any

from dandy.debug.debug import DebugRecorder
from dandy.debug.events import SuccessEvent, RunEvent
from dandy.handler.events import HandlerRunEvent


class ProcessDebugABCMeta(ABCMeta):
    def __new__(cls, name, bases, dct):
        # Wrap the process method to add logging
        if 'process' in dct:
            original_process = dct['process']

            # Ensure the method is a classmethod
            if isinstance(original_process, classmethod):
                original_func = original_process.__func__

                # Define a wrapper function that logs the method call
                def wrapped_process(cls, *args, **kwargs):
                    if DebugRecorder.is_recording and not getattr(cls, "_debugger_called", False):
                        DebugRecorder.add_event(
                            RunEvent(
                                actor=cls.__name__,
                                action='Process',
                            )
                        )
                        cls._debugger_called = True

                    result = original_func(cls, *args, **kwargs)

                    cls._debugger_called = False  # Reset only if this is the base class

                    return result

                # Reassign the wrapped function back as a classmethod
                dct['process'] = classmethod(wrapped_process)

        return super().__new__(cls, name, bases, dct)


class Handler(metaclass=ProcessDebugABCMeta):

    @classmethod
    @abstractmethod
    def process(cls, **kwargs: Any) -> Any:
        ...
