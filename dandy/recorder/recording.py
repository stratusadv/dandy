from datetime import datetime

from pydantic import BaseModel, Field

from dandy.recorder.events import EventManager


class Recording(BaseModel):
    name: str
    is_running: bool = False
    start_datetime: datetime = Field(default_factory=datetime.now)
    stop_datetime: datetime = Field(default_factory=datetime.now)
    run_time_seconds: float = 0.0
    event_manager: EventManager = Field(default_factory=EventManager)

    def clear(self):
        self.start_datetime = datetime.now()
        self.stop_datetime = datetime.now()

    def start(self):
        self.start_datetime = datetime.now()
        self.is_running = True

    def stop(self):
        self.stop_datetime = datetime.now()
        self.run_time_seconds = (self.stop_datetime - self.start_datetime).total_seconds()
        self.is_running = False