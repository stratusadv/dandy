from dandy.debug.event import BaseEvent, EventType


class BotEvent(BaseEvent):
    type: EventType = EventType.RUN