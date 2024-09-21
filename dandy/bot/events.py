from dandy.debug.events import BaseEvent, EventType


class BotEvent(BaseEvent):
    type: EventType = EventType.RUN