from dandy.recorder.events import Event, EventType

class CacheEvent(Event):
    object_name: str = 'Cache'
    response: str
    callable_name: str = 'Response'
    type: EventType = EventType.RESPONSE

