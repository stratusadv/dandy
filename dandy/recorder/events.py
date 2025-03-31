from enum import Enum
from time import time

from pydantic import BaseModel, Field
from typing_extensions import Union, Self


class EventType(str, Enum):
    RUN = 'run'
    RETRY = 'retry'
    REQUEST = 'request'
    RESPONSE = 'response'
    RESULT = 'result'
    SUCCESS = 'success'
    WARNING = 'warning'
    FAILURE = 'failure'
    OTHER = 'other'


class BaseEvent(BaseModel):
    actor: str
    action: str
    type: EventType
    time: float = Field(default_factory=time)
    run_time: float = 0.0
    description: Union[str, None] = None
    id: str = '-'

    def calculate_run_time(self, pre_event: Self):
        self.run_time = self.time - pre_event.time


class ResultEvent(BaseEvent):
    type: EventType = EventType.RESULT


class RunEvent(BaseEvent):
    type: EventType = EventType.RUN


class SuccessEvent(BaseEvent):
    type: EventType = EventType.SUCCESS


class WarningEvent(BaseEvent):
    type: EventType = EventType.WARNING


class FailureEvent(BaseEvent):
    type: EventType = EventType.FAILURE


class OtherEvent(BaseEvent):
    type: EventType = EventType.OTHER
