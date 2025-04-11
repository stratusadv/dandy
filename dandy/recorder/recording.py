from datetime import datetime

from pydantic import BaseModel, Field

from dandy.recorder.events import EventStore


class Recording(BaseModel):
    name: str
    is_running: bool = False
    start_datetime: datetime = Field(default_factory=datetime.now)
    stop_datetime: datetime = Field(default_factory=datetime.now)
    token_usage: int = 0
    run_time_seconds: float = 0.0
    event_count: int = 0
    event_store: EventStore = Field(default_factory=EventStore)

    def clear(self):
        self.start_datetime = datetime.now()
        self.stop_datetime = datetime.now()

    def start(self):
        self.start_datetime = datetime.now()
        self.is_running = True

    def stop(self):
        self.stop_datetime = datetime.now()
        self.run_time_seconds = self.event_store.events_total_run_time
        self.token_usage = self.event_store.events_total_token_usage
        self.event_count = self.event_store.event_count
        self.is_running = False