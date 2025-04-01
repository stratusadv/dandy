import json
from abc import ABCMeta

from dandy.core.utils import json_default
from dandy.recorder.recorder import Recorder
from dandy.recorder.events import Event, EventType
from dandy.recorder.utils import generate_new_recorder_event_id
from dandy.utils import pascal_to_title_case


class ProcessorABCMeta(ABCMeta):
    def __new__(cls, name, bases, dct):
        processor_class = super().__new__(cls, name, bases, dct)

        if 'process' in dct:
            original_process = dct['process']

            if isinstance(original_process, classmethod):
                original_func = original_process.__func__

                def wrapped_process(cls, *args, **kwargs):
                    if getattr(cls, "_debugger_called", None) is None:
                        cls._debugger_event_id = generate_new_recorder_event_id()

                    if Recorder.is_recording and not getattr(cls, "_debugger_called", False):
                        run_event = Event(
                            id=cls._debugger_event_id,
                            object_name=pascal_to_title_case(cls.__name__),
                            callable_name='Process',
                            type=EventType.RUN,
                        )

                        run_event.add_item(
                            key='description',
                            value=json.dumps(
                                {
                                    'args': args,
                                    'kwargs': kwargs
                                },
                                indent=4,
                                default=json_default
                            )
                        )

                        Recorder.add_event(run_event)

                        cls._debugger_called = True

                    result = original_func(cls, *args, **kwargs)

                    if Recorder.is_recording and getattr(cls, "_debugger_called", True):
                        result_event = Event(
                            id=cls._debugger_event_id,
                            object_name=pascal_to_title_case(cls.__name__),
                            callable_name='Process Returned Result',
                            type=EventType.RESULT,
                        )

                        result_event.add_item(
                            key='description',
                            value=json.dumps(
                                {
                                    'returned result': result
                                },
                                indent=4,
                                default=json_default
                            ),
                        )

                        Recorder.add_event(result_event)

                        cls._debugger_called = False

                    return result

                setattr(processor_class, 'process', classmethod(wrapped_process))

        return processor_class
