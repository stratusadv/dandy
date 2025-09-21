from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from dandy.recorder.events import EventAttribute, Event, EventType
from dandy.recorder.recorder import Recorder

if TYPE_CHECKING:
    from dandy.processor.map.map import Map


def recorder_add_process_map_value_event(
        map: Map,
        event_id: str,
        mapping_name: str | None = None,
):
    Recorder.add_event(
        Event(
            id=event_id,
            object_name=map.__class__.__name__,
            callable_name=f'Processing "{mapping_name}" Mapping' if mapping_name else 'Processing Mapping',
            type=EventType.OTHER,
            attributes=[
                EventAttribute(
                    key='Mapping Key Description',
                    value=map.mapping_keys_description,
                ),
                EventAttribute(
                    key='Mapping',
                    value=map.mapping,
                ),
            ]
        )
    )

def recorder_add_chosen_mappings_event(
        map: Map,
        chosen_mappings: dict[Any, str],
        event_id: str,
):
    chosen_mappings = {
        str(key): value for key, value in chosen_mappings.items()
    }

    Recorder.add_event(
        Event(
            id=event_id,
            object_name=map.__class__.__name__,
            callable_name=f'Finished Selecting Value(s) from Mapping',
            type=EventType.OTHER,
            attributes=[
                EventAttribute(
                    key='Chosen Mapping Keys',
                    value=json.dumps(chosen_mappings, indent=4),
                ),
            ]
        )
    )
