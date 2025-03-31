from pydantic import BaseModel

from dandy.constants import __VERSION__

from datetime import datetime
from pathlib import Path

from dandy.recorder.renderer.renderer import BaseRecordingRenderer
from dandy.recorder.utils import generate_new_recorder_event_id


class JsonRecordingRenderer(BaseRecordingRenderer):
    def _render_json_to_str(self) -> str:
        return self.recording.model_dump_json()

    def to_file(
            self,
            path: str,
            file_name: str,
    ):
        Path(path).mkdir(parents=True, exist_ok=True)

        with open(Path(path, file_name), 'w') as new_file:
            new_file.write(self.to_str())

    def to_str(self) -> str:
        return self._render_json_to_str()

