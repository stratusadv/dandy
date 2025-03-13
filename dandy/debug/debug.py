import json
from datetime import datetime
from pathlib import Path
from time import perf_counter

from pydantic import BaseModel, Field
from typing_extensions import Dict, List, Union

from dandy.conf import settings
from dandy.constants import DEBUG_OUTPUT_DIRECTORY, __VERSION__
from dandy.core.singleton import Singleton
from dandy.debug.events import BaseEvent
from dandy.debug.exceptions import DebugCriticalException
from dandy.debug.utils import generate_new_debug_event_id

_DEFAULT_DEBUG_OUTPUT_PATH = Path(settings.BASE_PATH, DEBUG_OUTPUT_DIRECTORY)


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

    def start(self):
        self.start_time = perf_counter()
        self.is_recording = True

    def stop(self):
        self.stop_time = perf_counter()
        self.run_time = self.stop_time - self.start_time
        self.calculate_event_run_times()
        self.is_recording = False

    @staticmethod
    def to_file(
            path: Union[str, Path],
            file_name: str,
            value: str
    ):

        Path(path).mkdir(parents=True, exist_ok=True)

        with open(Path(path, file_name), 'w') as new_file:
            new_file.write(value)

    def to_html_file(self, path: Union[str, Path] = _DEFAULT_DEBUG_OUTPUT_PATH):
        self.to_file(
            path=path,
            file_name=f'{self.name}_debug_output.html',
            value=self.to_html_str()
        )

    def to_html_str(self) -> str:
        if self.is_recording:
            self.stop()

        with open(Path(Path(__file__).parent.resolve(), 'html', 'debug_recorder_output_template.html'),
                  'r') as debug_html:
            return debug_html.read(
            ).replace(
                '__debug_output__',
                self.model_dump_json(),
            ).replace(
                '__debug_version__',
                f'{__VERSION__}'
            ).replace(
                '__debug_datetime__',
                f'{datetime.now()}'
            ).replace(
                '__debug_event_id__',
                f'{generate_new_debug_event_id()}'
            )

    def to_json_file(self, path: Union[str, Path] = _DEFAULT_DEBUG_OUTPUT_PATH):
        self.to_file(
            path=path,
            file_name=f'{self.name}_debug_output.json',
            value=self.to_json_str()
        )

    def to_json_str(self) -> str:
        return self.model_dump_json(indent=4)


class DebugRecorder(Singleton):
    debuggers: Dict[str, Debugger] = dict()

    @classmethod
    def _recording_allowed(cls) -> bool:
        return settings.ALLOW_DEBUG_RECORDING

    @classmethod
    def add_event(cls, event: BaseEvent):
        if cls._recording_allowed():
            for debugger in cls.debuggers.values():
                if debugger.is_recording:
                    debugger.add_event(event)

    @classmethod
    def clear(cls):
        if cls._recording_allowed():
            cls.debuggers = dict()

    @classmethod
    def start_recording(cls, debugger_name: str = 'default'):
        if cls._recording_allowed():
            cls.debuggers[debugger_name] = Debugger(name=debugger_name)
            cls.debuggers[debugger_name].start()

    @classmethod
    def stop_recording(cls, debugger_name: str = 'default'):
        if cls._recording_allowed():
            if debugger_name not in cls.debuggers:
                choices_message = ''

                if len(cls.debuggers.keys()) == 0:
                    choices_message = f' Choices are {list(cls.debuggers.keys())}'

                raise DebugCriticalException(f'Debug recording "{debugger_name}" does not exist. {choices_message}')

            cls.debuggers[debugger_name].stop()

    @classmethod
    def stop_all_recording(cls):
        if cls._recording_allowed():
            for debugger in cls.debuggers.values():
                debugger.stop()

    @classmethod
    @property
    def is_recording(cls):
        if cls._recording_allowed():
            return any([debugger.is_recording for debugger in cls.debuggers.values()])

    @classmethod
    def to_html_file(cls, debugger_name: str = 'default', path=_DEFAULT_DEBUG_OUTPUT_PATH):
        if cls._recording_allowed():
            cls.debuggers[debugger_name].to_html_file(path)

    @classmethod
    def to_html_str(cls, debugger_name: str = 'default') -> str:
        if cls._recording_allowed():
            return cls.debuggers[debugger_name].to_html_str()
        else:
            return 'DEBUG RECORDING DISABLED'

    @classmethod
    def to_json_file(cls, debugger_name: str = 'default', path=_DEFAULT_DEBUG_OUTPUT_PATH):
        if cls._recording_allowed():
            cls.debuggers[debugger_name].to_json_file(path)

    @classmethod
    def to_json_str(cls, debugger_name: str = 'default') -> str:
        if cls._recording_allowed():
            return cls.debuggers[debugger_name].to_json_str()
        else:
            return json.dumps({'output': 'DEBUG RECORDING DISABLED'}, indent=4)
