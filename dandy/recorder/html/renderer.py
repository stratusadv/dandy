from dandy.constants import __VERSION__

from datetime import datetime
from pathlib import Path

from dandy.recorder.recording import Recording
from dandy.recorder.utils import generate_new_recorder_event_id


class HtmlRenderer:
    template_directory = Path(Path(__file__).parent.resolve(), 'templates')

    @classmethod
    def render(cls, recording: Recording) -> str:
        return cls.render_base_template(recording)

    @classmethod
    def render_base_template(cls, recording: Recording) -> str:
        with open(Path(cls.template_directory, 'base_recording_output_template.html'),
                  'r') as debug_html:
            return debug_html.read(
            ).replace(
                '__recording_json_output__',
                recording.model_dump_json(),
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
                cls.render_event_templates()
            )

    @classmethod
    def render_event_templates(cls) -> str:
        output = ''

        event_templates = [item.name for item in Path(cls.template_directory, 'event').iterdir() if item.is_file()]

        for event_template in event_templates:
            with (open(Path(cls.template_directory, 'event', event_template), 'r') as event_template_html):
                output += event_template_html.read()

        return output
