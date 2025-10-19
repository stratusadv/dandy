from __future__ import annotations

import functools
import json
from typing import Callable, TYPE_CHECKING

from dandy.core.utils import pascal_to_title_case
from dandy.recorder.events import Event, EventType, EventAttribute
from dandy.recorder.recorder import Recorder
from dandy.recorder.utils import generate_new_recorder_event_id, json_default

if TYPE_CHECKING:
    from dandy.processor.processor import BaseProcessor

def record_process_wrapper(self: BaseProcessor, method: Callable) -> Callable:
    @functools.wraps(method)
    def wrapper(*args, **kwargs) -> Callable:
        if getattr(self, "_recorder_called", None) is None:
            self._recorder_event_id = generate_new_recorder_event_id()

        if Recorder.is_recording and not getattr(self, "_recorder_called", False):
            Recorder.add_event(
                Event(
                    id=self._recorder_event_id,
                    object_name=pascal_to_title_case(self.__class__.__qualname__),
                    callable_name='Process',
                    type=EventType.RUN,
                    attributes=[
                        EventAttribute(
                            key='Module',
                            value=self.__class__.__module__,
                        ),
                        EventAttribute(
                            key='Args',
                            value=json.dumps(
                                args,
                                indent=4,
                                default=json_default
                            ),
                            is_card=True
                        ),
                        EventAttribute(
                            key='Kwargs',
                            value=json.dumps(
                                kwargs,
                                indent=4,
                                default=json_default
                            ),
                            is_card=True
                        )
                    ],
                )
            )

            self._recorder_called = True

        result = method(*args, **kwargs)

        if Recorder.is_recording and getattr(self, "_recorder_called", True):
            Recorder.add_event(
                Event(
                    id=self._recorder_event_id,
                    object_name=pascal_to_title_case(self.__class__.__qualname__),
                    callable_name='Process Returned Result',
                    type=EventType.RESULT,
                    attributes=[
                        EventAttribute(
                            key='Module',
                            value=self.__class__.__module__,
                        ),
                        EventAttribute(
                            key='Returned Result',
                            value=json.dumps(
                                result,
                                indent=4,
                                default=json_default
                            ),
                            is_card=True,
                        )
                    ],
                )
            )
            self._recorder_called = False

        return result

    return wrapper

