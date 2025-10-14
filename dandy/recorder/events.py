import logging
from enum import Enum
from time import perf_counter

from pydantic import BaseModel, Field
from typing import Self, Any

from dandy.conf import settings


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


class EventAttribute(BaseModel):
    key: str
    value: Any
    is_dropdown: bool = False
    is_card: bool = False
    is_base64_image: bool = False


class Event(BaseModel):
    id: str
    object_name: str
    callable_name: str
    type: EventType
    attributes: list[EventAttribute] | None = Field(default_factory=list)
    start_time: float = Field(default_factory=perf_counter)
    token_usage: int = 0
    run_time_seconds: float = 0.0

    if settings.DEBUG:
        def model_post_init(self, __context: Any, /):
            logging.debug(str(self))

    def calculate_run_time(self, pre_event: Self):
        self.run_time_seconds = self.start_time - pre_event.start_time

    def add_attribute(self, event_attribute: EventAttribute) -> Self:
        self.attributes.append(event_attribute)

        return self


class EventStore(BaseModel):
    events: list[Event] = Field(default_factory=list)

    def add_event(self, event: Event) -> Event:
        self.events.append(event)
        self._calculate_event_run_times()

        return event

    def _calculate_event_run_times(self):
        if len(self.events) > 0:
            self.events[0].run_time_seconds = 0.0
            for i in range(1, len(self.events)):
                self.events[i].calculate_run_time(self.events[i - 1])

    @property
    def event_count(self) -> int:
        return len(self.events)

    @property
    def events_total_run_time(self) -> float:
        return sum(event.run_time_seconds for event in self.events)

    @property
    def events_total_token_usage(self) -> int:
        return sum(event.token_usage for event in self.events)
