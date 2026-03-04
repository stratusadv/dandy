from dandy import Recorder
from dandy.recorder.events import Event, EventType, EventAttribute


def recorder_add_llm_diligence_event(
        event_id: str,
        diligence_name: str,
        event_attributes: list[EventAttribute],
) -> None:
    Recorder.add_event(
        Event(
            id=event_id,
            object_name='LLM Diligence',
            callable_name=diligence_name,
            type=EventType.OTHER,
            attributes=event_attributes,
        )
    )
