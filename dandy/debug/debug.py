import json
from datetime import datetime
from pathlib import Path
from random import choices
from time import time
from typing_extensions import Dict, List

from pydantic import BaseModel, Field

from dandy.core.singleton import Singleton
from dandy.debug.events import BaseEvent
from dandy.debug.exceptions import DebugException
from dandy.debug.utils import generate_new_debug_event_id


class Debugger(BaseModel):
    name: str
    is_recording: bool = False
    start_time: float = 0.0
    stop_time: float = 0.0
    run_time: float = 0.0
    events: List = Field(default_factory=list)

    def add_event(
            self,
            event: BaseEvent
    ) -> str:
        self.events.append(event)

        return event.id

    def calculate_event_run_times(self):
        if len(self.events) > 0:
            self.events[0].run_time = 0.0
            for i in range(1, len(self.events)):
                self.events[i].calculate_run_time(self.events[i - 1])

    def clear(self):
        self.start_time = 0.0
        self.stop_time = 0.0
        self.event_manager.clear()

    def start(self):
        self.start_time = time()
        self.is_recording = True

    def stop(self):
        self.stop_time = time()
        self.run_time = self.stop_time - self.start_time
        self.calculate_event_run_times()
        self.is_recording = False

    def to_html_file(self, path=''):
        with open(Path(path, f'{self.name}_debug_output.html'), 'w') as new_debug_html:
            new_debug_html.write(self.to_html_str())

    def to_html_str(self) -> str:
        if self.is_recording:
            self.stop()

        with open(Path(Path(__file__).parent.resolve(), 'html', 'debug_recorder_output_template.html'), 'r') as debug_html:
            return debug_html.read(
            ).replace(
                '__debug_output__',
                self.model_dump_json(),
            ).replace(
                '__debug_datetime__',
                f'{datetime.now()}'
            ).replace(
                '__debug_event_id__',
                f'{generate_new_debug_event_id()}'
            )


class DebugRecorder(Singleton):
    debuggers: Dict[str, Debugger] = dict()

    @classmethod
    def add_event(cls, event: BaseEvent):
        for debugger in cls.debuggers.values():
            if debugger.is_recording:
                debugger.add_event(event)

    @classmethod
    def clear(cls):
        cls.debuggers = dict()

    @classmethod
    def start_recording(cls, name: str = 'default'):
        cls.debuggers[name] = Debugger(name=name)
        cls.debuggers[name].start()

    @classmethod
    def stop_recording(cls, name: str = 'default'):
        if name not in cls.debuggers:
            choices_message = ''

            if len(cls.debuggers.keys()) == 0:
                choices_message = f' Choices are {list(cls.debuggers.keys())}'

            raise DebugException(f'Debug recording "{name}" does not exist. {choices_message}')

        cls.debuggers[name].stop()

    @classmethod
    def stop_all_recording(cls):
        for debugger in cls.debuggers.values():
            debugger.stop()

    @classmethod
    @property
    def is_recording(cls):
        return any([debugger.is_recording for debugger in cls.debuggers.values()])

    @classmethod
    def to_html_file(cls, name: str = 'default',  path=''):
        cls.debuggers[name].to_html_file(path)

    @classmethod
    def to_html_str(cls, name: str = 'default') -> str:
        return cls.debuggers[name].to_html_str()
