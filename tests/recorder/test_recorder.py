from pathlib import Path
from unittest import TestCase

from dandy.constants import RECORDING_POSTFIX_NAME
from dandy.bot.bot import Bot
from dandy.intel.intel import BaseIntel
from dandy.recorder.decorators import recorder_to_html_file, recorder_to_json_file, \
    recorder_to_markdown_file
from dandy.recorder.exceptions import RecorderCriticalError
from dandy.recorder.recorder import Recorder, DEFAULT_RECORDER_OUTPUT_PATH

RENDERER_AND_EXTENSIONS = (
    ('html', '.html'),
    ('json', '.json'),
    ('markdown', '.md'),
)

RECORDING_NAME = 'test_recorder'

RECORDING_OUTPUT_FILE_PATH = Path(
    DEFAULT_RECORDER_OUTPUT_PATH,
    f'{RECORDING_NAME}{RECORDING_POSTFIX_NAME}',
)

def get_capital_intel(country: str) -> BaseIntel:
    capital_city_intel = Bot().llm.prompt_to_intel(
        prompt=f'Please tell me just the name only of the city that is the capital of {country}?'
    )

    return Bot().llm.prompt_to_intel(
        prompt=f'Please describe the following city: {capital_city_intel.text}'
    )


class TestRecorder(TestCase):
    @classmethod
    def setUpClass(cls):
        for _, extension in RENDERER_AND_EXTENSIONS:
            if Path(RECORDING_OUTPUT_FILE_PATH.with_suffix(extension)).is_file():
                Path(RECORDING_OUTPUT_FILE_PATH.with_suffix(extension)).unlink()

    def test_recorder(self):

        Recorder.start_recording(RECORDING_NAME)

        _ = get_capital_intel('Canada')

        Recorder.stop_recording(RECORDING_NAME)

        self.assertTrue(Recorder.to_html_str(RECORDING_NAME) != '')

    def test_record_to_html_file_decorator(self):
        @recorder_to_html_file(RECORDING_NAME)
        def html_function():
            _ = get_capital_intel('Canada')

        html_function()

        with open(RECORDING_OUTPUT_FILE_PATH.with_suffix('.html'), 'r') as f:
            self.assertTrue(f.read() != '')

    def test_record_to_json_file_decorator(self):
        @recorder_to_json_file(RECORDING_NAME)
        def json_function():
            _ = get_capital_intel('Canada')

        json_function()

        with open(RECORDING_OUTPUT_FILE_PATH.with_suffix('.json'), 'r') as f:
            self.assertTrue(f.read() != '')

    def test_record_to_md_file_decorator(self):
        @recorder_to_markdown_file(RECORDING_NAME)
        def markdown_function():
            _ = get_capital_intel('Canada')

        markdown_function()

        with open(RECORDING_OUTPUT_FILE_PATH.with_suffix('.md'), 'r') as f:
            self.assertTrue(f.read() != '')

    def test_no_event_recording(self):
        Recorder.start_recording(RECORDING_NAME)
        Recorder.stop_recording(RECORDING_NAME)

        self.assertTrue(Recorder.to_html_str(RECORDING_NAME) != '')

    def test_recording_to_str(self):
        Recorder.start_recording(RECORDING_NAME)

        _ = get_capital_intel('Canada')

        Recorder.stop_recording(RECORDING_NAME)

        for renderer, _ in RENDERER_AND_EXTENSIONS:
            render_method = getattr(Recorder, f'to_{renderer}_str')
            self.assertTrue(render_method(RECORDING_NAME) != '')
            self.assertTrue(render_method(RECORDING_NAME) is not None)

    def test_recorder_to_file_with_emoji(self):
        Recorder.start_recording(RECORDING_NAME)

        _ = Bot().llm.prompt_to_intel(
            # This another prompt that seems to freeze the LLM indefinitely !!!
            # prompt='How many countries are in the 🌎? please respond with emojis!',
            prompt='How many countries are in the 🌎? please respond with numbers and emojis!',
        )

        Recorder.stop_recording(RECORDING_NAME)

        for renderer, extension in RENDERER_AND_EXTENSIONS:
            render_method = getattr(Recorder, f'to_{renderer}_file')

            render_method(
                RECORDING_NAME,
                DEFAULT_RECORDER_OUTPUT_PATH,
            )

            with open(
                    RECORDING_OUTPUT_FILE_PATH.with_suffix(extension),
                    'r',
                    encoding='utf-8'
            ) as f:
                self.assertTrue(f.read() != '')

    def test_invalid_recorder_name_throws_critical_exception(self):
        Recorder.start_recording(RECORDING_NAME)
        Recorder.stop_recording(RECORDING_NAME)

        Recorder.check_recording_is_valid(RECORDING_NAME)

        invalid_recorder_name = f'invalid_{RECORDING_NAME}'

        with self.assertRaises(RecorderCriticalError):
            Recorder.check_recording_is_valid(invalid_recorder_name)
