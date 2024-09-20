from dandy.debug.event import BaseEvent, EventType


class WorkflowEvent(BaseEvent):
    type: EventType = EventType.RUN