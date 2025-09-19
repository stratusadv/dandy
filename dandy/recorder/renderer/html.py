from datetime import datetime
from pathlib import Path

from dandy.consts import __VERSION__, RECORDING_POSTFIX_NAME
from dandy.recorder.renderer.renderer import BaseRecordingRenderer
from dandy.recorder.utils import generate_new_recorder_event_id


class HtmlRecordingRenderer(BaseRecordingRenderer):
    name: str = 'html'
    file_extension: str = 'html'

    _template_directory: Path = Path(Path(__file__).parent.resolve(), 'html_templates')

    def _render_base_html_template_to_str(self) -> str:
        with open(Path(self._template_directory, 'base_recording_output_template.html'),
                  'r') as debug_html:
            return debug_html.read(
            ).replace(
                '__recording_json__',
                self.recording.model_dump_json(indent=4),
            ).replace(
                '__dandy_version__',
                f'{__VERSION__}'
            ).replace(
                '__recording_datetime__',
                f'{self.recording.start_datetime.strftime("%Y-%m-%d %H:%M")}'
            ).replace(
                '__recording_id__',
                f'{generate_new_recorder_event_id()}'
            ).replace(
                '__recording_event_template__',
                self._render_event_html_template_to_str()
            )

    def _render_event_html_template_to_str(self) -> str:
        with open(Path(self._template_directory, 'base_event_template.html'), 'r') as event_template_html:
            return event_template_html.read()

    def to_file(
            self,
            path: Path | str
    ):
        Path(path).mkdir(parents=True, exist_ok=True)

        with open(
                Path(path, f'{self.recording.name}{RECORDING_POSTFIX_NAME}.html'),
                'w',
                encoding='utf-8'
        ) as new_file:
            new_file.write(self.to_str())

    def to_str(self) -> str:
        return self._render_base_html_template_to_str()
