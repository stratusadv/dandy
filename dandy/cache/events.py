from dandy.debug.events import BaseEvent, EventType

class CacheEvent(BaseEvent):
    actor: str = 'Cache'
    response: str
    action: str = 'Response'
    type: EventType = EventType.RESPONSE

