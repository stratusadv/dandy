from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from dandy.recorder.events import EventAttribute, Event, EventType
from dandy.recorder.recorder import Recorder

if TYPE_CHECKING:
    from dandy.processor.decoder.decoder import Decoder


def recorder_add_process_decoder_value_event(
        decoder: Decoder,
        event_id: str,
        mapping_name: str | None = None,
) -> None:

    processed_mapping = {}
    for key, value in decoder.mapping.items():
        if isinstance(value, (str, int, float)):
            processed_mapping[key] = value
        elif isinstance(value, type):
            processed_mapping[key] = value.__name__
        else:
            processed_mapping[key] = value.__class__.__name__

    Recorder.add_event(
        Event(
            id=event_id,
            object_name=decoder.__class__.__name__,
            callable_name=f'Processing "{mapping_name}" Mapping' if mapping_name else 'Processing Mapping',
            type=EventType.OTHER,
            attributes=[
                EventAttribute(
                    key='Mapping Key Description',
                    value=decoder.mapping_keys_description,
                ),
                EventAttribute(
                    key='Mapping',
                    value=json.dumps(processed_mapping, indent=4),
                ),
            ]
        )
    )

def recorder_add_chosen_mappings_event(
        decoder: Decoder,
        chosen_mappings: dict[Any, str],
        event_id: str,
) -> None:

    processed_chosen_mappings = {}
    for key, value in chosen_mappings.items():
        if isinstance(key, type):
            processed_chosen_mappings[key.__name__] = value
        else:
            processed_chosen_mappings[str(key)] = value

    Recorder.add_event(
        Event(
            id=event_id,
            object_name=decoder.__class__.__name__,
            callable_name='Finished Selecting Value(s) from Mapping',
            type=EventType.OTHER,
            attributes=[
                EventAttribute(
                    key='Chosen Mapping Keys',
                    value=json.dumps(processed_chosen_mappings, indent=4),
                ),
            ]
        )
    )
