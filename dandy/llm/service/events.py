from dandy.debug.events import BaseEvent, EventType

class LlmServiceEvent(BaseEvent):
    actor: str = 'LLM Service'


class LlmServiceFailureEvent(LlmServiceEvent):
    action: str = 'Failure'
    type: EventType = EventType.FAILURE


class LlmServiceRequestEvent(LlmServiceEvent):
    request: dict
    temperature: float
    estimated_tokens: int = 0
    action: str = 'Request'
    type: EventType = EventType.REQUEST


class LlmServiceResponseEvent(LlmServiceEvent):
    response: str
    estimated_tokens: int = 0
    action: str = 'Response'
    type: EventType = EventType.RESPONSE


class LlmServiceRetryEvent(LlmServiceEvent):
    action: str = 'Retry'
    type: EventType = EventType.RETRY


class LlmServiceSuccessEvent(LlmServiceEvent):
    action: str = 'Success'
    type: EventType = EventType.SUCCESS



