from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import List, Union

from pydantic import BaseModel, Field

from dandy.constants import __VERSION__
from dandy.recorder.events import BaseEvent
from dandy.recorder.recorder import _DEFAULT_DEBUG_OUTPUT_PATH
from dandy.recorder.utils import generate_new_recorder_event_id


class Recording(BaseModel):
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
                f'{generate_new_recorder_event_id()}'
            )

    def to_json_file(self, path: Union[str, Path] = _DEFAULT_DEBUG_OUTPUT_PATH):
        self.to_file(
            path=path,
            file_name=f'{self.name}_debug_output.json',
            value=self.to_json_str()
        )

    def to_json_str(self) -> str:
        return self.model_dump_json(indent=4)
