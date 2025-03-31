from pydantic import BaseModel

from dandy.constants import __VERSION__

from datetime import datetime
from pathlib import Path

from dandy.recorder.renderer.renderer import BaseRecordingRenderer
from dandy.recorder.utils import generate_new_recorder_event_id


class HtmlRecordingRenderer(BaseRecordingRenderer):
    _template_directory: Path = Path(Path(__file__).parent.resolve(), 'html_templates')

    def _render_base_html_template_to_str(self) -> str:
        with open(Path(self._template_directory, 'base', 'base_recording_output_template.html'),
                  'r') as debug_html:
            return debug_html.read(
            ).replace(
                '__recording_json_output__',
                self.recording.model_dump_json(),
            ).replace(
                '__dandy_version__',
                f'{__VERSION__}'
            ).replace(
                '__recording_datetime__',
                f'{datetime.now()}'
            ).replace(
                '__recording_event_id__',
                f'{generate_new_recorder_event_id()}'
            ).replace(
                '__recording_event_templates__',
                self._render_event_html_templates_to_str()
            )

    def _render_event_html_templates_to_str(self) -> str:
        output_str = ''

        event_templates = [item.name for item in Path(self._template_directory, 'event').iterdir() if item.is_file()]

        for event_template in event_templates:
            with (open(Path(self._template_directory, 'event', event_template), 'r') as event_template_html):
                output_str += event_template_html.read()

        return output_str

    def to_file(
            self,
            path: str,
            file_name: str,
    ):
        Path(path).mkdir(parents=True, exist_ok=True)

        with open(Path(path, file_name), 'w') as new_file:
            new_file.write(self.to_str())

    def to_str(self) -> str:
        return self._render_base_html_template_to_str()

