import json
from abc import ABCMeta

from dandy.core.utils import json_default
from dandy.debug.debug import DebugRecorder
from dandy.debug.events import RunEvent, ResultEvent
from dandy.debug.utils import generate_new_debug_event_id
from dandy.utils import pascal_to_title_case


class ProcessorABCMeta(ABCMeta):
    def __new__(cls, name, bases, dct):
        if 'process' in dct:
            original_process = dct['process']

            if isinstance(original_process, classmethod):
                original_func = original_process.__func__

                def wrapped_process(cls, *args, **kwargs):
                    if getattr(cls, "_debugger_called", None) is None:
                        cls._debugger_event_id = generate_new_debug_event_id()

                    if DebugRecorder.is_recording and not getattr(cls, "_debugger_called", False):
                        DebugRecorder.add_event(
                            RunEvent(
                                actor=pascal_to_title_case(cls.__name__),
                                action='Process',
                                description=json.dumps(
                                    {
                                        'args': args,
                                        'kwargs': kwargs
                                    },
                                    indent=4,
                                    default=json_default
                                ),
                                id=cls._debugger_event_id
                            )
                        )
                        cls._debugger_called = True

                    result = original_func(cls, *args, **kwargs)

                    if DebugRecorder.is_recording and getattr(cls, "_debugger_called", True):
                        DebugRecorder.add_event(
                            ResultEvent(
                                actor=pascal_to_title_case(cls.__name__),
                                action='Process Returned Result',
                                description=json.dumps(
                                    {
                                        'returned result': result
                                    },
                                    indent=4,
                                    default=json_default
                                ),
                                id=cls._debugger_event_id
                            )
                        )

                    cls._debugger_called = False

                    return result

                dct['process'] = classmethod(wrapped_process)

        return super().__new__(cls, name, bases, dct)

