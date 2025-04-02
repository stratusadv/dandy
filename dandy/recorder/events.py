from abc import ABC
from enum import Enum
from time import perf_counter

from pydantic import BaseModel, Field
from typing_extensions import Union, Self, Dict, Any, List


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


class EventItem(BaseModel):
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
    items: List[EventItem] = Field(default_factory=list)
    start_time: float = Field(default_factory=perf_counter)
    run_time: float = 0.0

    def calculate_run_time(self, pre_event: Self):
        self.run_time = self.start_time - pre_event.start_time

    def add_item(self, event_item: EventItem) -> Self:
        self.items.append(event_item)

        return self


class EventManager(BaseModel):
    events: List[Event] = Field(default_factory=list)

    def add_event(self, event: Event) -> Event:
        self.events.append(event)
        self._calculate_event_run_times()

        return event

    def _calculate_event_run_times(self):
        if len(self.events) > 0:
            self.events[0].run_time = 0.0
            for i in range(1, len(self.events)):
                self.events[i].calculate_run_time(self.events[i - 1])
