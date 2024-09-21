from enum import Enum
from time import time
from typing import List, Any, Dict

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
    type: EventType
    time: float = Field(default_factory=time)


class RunEvent(BaseEvent):
    type: EventType = EventType.RUN


class SuccessEvent(BaseEvent):
    type: EventType = EventType.SUCCESS


class FailureEvent(BaseEvent):
    type: EventType = EventType.FAILURE
