from dandy.recorder.events import Event, EventType

class LlmServiceEvent(Event):
    object_name: str = 'LLM Service'


class LlmServiceFailureEvent(LlmServiceEvent):
    callable_name: str = 'Failure'
    type: EventType = EventType.FAILURE


class LlmServiceRequestEvent(LlmServiceEvent):
    request: dict
    temperature: float
    estimated_tokens: int = 0
    json_schema: str = ''
    callable_name: str = 'Request'
    type: EventType = EventType.REQUEST


class LlmServiceResponseEvent(LlmServiceEvent):
    response: str
    estimated_tokens: int = 0
    callable_name: str = 'Response'
    type: EventType = EventType.RESPONSE


class LlmServiceRetryEvent(LlmServiceEvent):
    callable_name: str = 'Retry'
    type: EventType = EventType.RETRY


class LlmServiceSuccessEvent(LlmServiceEvent):
    callable_name: str = 'Success'
    type: EventType = EventType.SUCCESS



