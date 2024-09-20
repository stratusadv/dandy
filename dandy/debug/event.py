from enum import Enum
from time import time
from typing import List, Any

from pydantic import BaseModel, Field


class EventType(str, Enum):
    RUN = 'run'
    RETRY = 'retry'
    REQUEST = 'request'
    RESPONSE = 'response'
    SUCCESS = 'success'
    FAILURE = 'failure'


class BaseEvent(BaseModel):
    actor: str
    action: str
    type: EventType = EventType.RUN
    time: float = Field(default_factory=time)


class SuccessEvent(BaseEvent):
    type: EventType = EventType.SUCCESS


class FailureEvent(BaseEvent):
    type: EventType = EventType.FAILURE
