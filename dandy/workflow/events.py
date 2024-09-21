from dandy.debug.events import BaseEvent, EventType


class WorkflowEvent(BaseEvent):
    type: EventType = EventType.RUN