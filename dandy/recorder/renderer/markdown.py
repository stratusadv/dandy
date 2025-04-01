from pydantic import BaseModel

from dandy.constants import __VERSION__

from datetime import datetime
from pathlib import Path

from dandy.recorder.renderer.renderer import BaseRecordingRenderer
from dandy.recorder.utils import generate_new_recorder_event_id


class MarkdownRecordingRenderer(BaseRecordingRenderer):
    def _render_markdown_to_str(self) -> str:
        return f'{self.recording.name}'

    def to_file(
            self,
            path: Path,
    ):
        Path(path).mkdir(parents=True, exist_ok=True)

        with open(Path(path, f'{self.recording.name}_recording_output.md'), 'w') as new_file:
            new_file.write(self.to_str())

    def to_str(self) -> str:
        return self._render_markdown_to_str()

