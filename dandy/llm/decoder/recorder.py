from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from dandy.recorder.events import EventAttribute, Event, EventType
from dandy.recorder.recorder import Recorder

if TYPE_CHECKING:
    from dandy.llm.decoder.decoder import Decoder


_EVENT_OBJECT_NAME = 'Decoder Service'


def recorder_add_process_decoder_value_event(
        decoder: Decoder,
        event_id: str,
) -> None:

    processed_mapping = {}
    for key, value in decoder.keys_values.items():
        if isinstance(value, (str, int, float)):
            processed_mapping[key] = value
        elif isinstance(value, type):
            processed_mapping[key] = value.__name__
        else:
            processed_mapping[key] = value.__class__.__name__

    Recorder.add_event(
        Event(
            id=event_id,
            object_name=_EVENT_OBJECT_NAME,
            callable_name=f'Processing "{decoder.keys_description}"',
            type=EventType.OTHER,
            attributes=[
                EventAttribute(
                    key='Keys Description',
                    value=decoder.keys_description,
                ),
                EventAttribute(
                    key='Keys Values',
                    value=json.dumps(processed_mapping, indent=4),
                ),
            ]
        )
    )

def recorder_add_chosen_values_event(
        chosen_values_keys: dict[Any, str],
        event_id: str,
) -> None:

    processed_chosen_mappings = {}
    for key, value in chosen_values_keys.items():
        if isinstance(key, type):
            processed_chosen_mappings[key.__name__] = value
        else:
            processed_chosen_mappings[str(key)] = value

    Recorder.add_event(
        Event(
            id=event_id,
            object_name=_EVENT_OBJECT_NAME,
            callable_name='Finished Selecting Value(s)',
            type=EventType.OTHER,
            attributes=[
                EventAttribute(
                    key='Chosen Values Keys',
                    value=json.dumps(processed_chosen_mappings, indent=4),
                ),
            ]
        )
    )
