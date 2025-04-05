from pathlib import Path

from typing_extensions import Dict, Type

from dandy.conf import settings
from dandy.constants import RECORDER_OUTPUT_DIRECTORY, RECORDING_DEFAULT_NAME
from dandy.core.singleton import Singleton
from dandy.recorder.events import Event
from dandy.recorder.exceptions import RecorderCriticalException
from dandy.recorder.recording import Recording
from dandy.recorder.renderer.html import HtmlRecordingRenderer
from dandy.recorder.renderer.json import JsonRecordingRenderer
from dandy.recorder.renderer.markdown import MarkdownRecordingRenderer
from dandy.recorder.renderer.renderer import BaseRecordingRenderer

DEFAULT_RECORDER_OUTPUT_PATH = Path(settings.BASE_PATH, RECORDER_OUTPUT_DIRECTORY)


class Recorder(Singleton):
    recordings: Dict[str, Recording] = dict()
    renderers: Dict[str, Type[BaseRecordingRenderer]] = {
        'html': HtmlRecordingRenderer,
        'json': JsonRecordingRenderer,
        'markdown': MarkdownRecordingRenderer,
    }

    @classmethod
    def add_event(cls, event: Event):
        for recording in cls.recordings.values():
            if recording.is_running:
                recording.event_manager.add_event(event)

    @classmethod
    def check_recording_is_valid(cls, recording_name: str = RECORDING_DEFAULT_NAME):
        if recording_name not in cls.recordings:
            choices_message = ''

            if len(cls.recordings.keys()) == 0:
                choices_message = f' Choices are {list(cls.recordings.keys())}'

            raise RecorderCriticalException(f'Recording "{recording_name}" does not exist. {choices_message}')

    @classmethod
    def clear(cls):
        cls.recordings = dict()

    @classmethod
    def is_recording(cls):
        return any([recording.is_running for recording in cls.recordings.values()])

    @classmethod
    def start_recording(cls, recording_name: str = RECORDING_DEFAULT_NAME):
        cls.recordings[recording_name] = Recording(name=recording_name)
        cls.recordings[recording_name].start()

    @classmethod
    def stop_recording(cls, recording_name: str = RECORDING_DEFAULT_NAME):
        cls.check_recording_is_valid(recording_name)
        cls.recordings[recording_name].stop()

    @classmethod
    def stop_all_recording(cls):
        for recording in cls.recordings.values():
            recording.stop()

    @classmethod
    def _render(
            cls,
            to_file: bool,
            renderer: str,
            recording_name: str = RECORDING_DEFAULT_NAME,
            path: Path | str = DEFAULT_RECORDER_OUTPUT_PATH
    ) -> str | None:
        if renderer not in cls.renderers:
            raise RecorderCriticalException(
                f'Renderer "{renderer}" does not exist. Choices are {list(cls.renderers.keys())}')

        cls.check_recording_is_valid(recording_name)

        if to_file:
            cls.renderers[renderer](
                recording=cls.recordings[recording_name]
            ).to_file(path)
        else:
            return cls.renderers[renderer](
                recording=cls.recordings[recording_name]
            ).to_str()

    @classmethod
    def _to_file(
            cls,
            recording_name: str,
            renderer: str,
            path: Path | str
    ):
        return cls._render(
            to_file=True,
            renderer=renderer,
            recording_name=recording_name,
            path=path
        )

    @classmethod
    def _to_str(
            cls,
            recording_name: str,
            renderer: str,
    ):
        return cls._render(
            to_file=False,
            renderer=renderer,
            recording_name=recording_name,
        )

    @classmethod
    def to_html_file(
            cls,
            recording_name: str = RECORDING_DEFAULT_NAME,
            path: Path | str = DEFAULT_RECORDER_OUTPUT_PATH
    ):
        cls._to_file(
            recording_name,
            'html',
            path
        )

    @classmethod
    def to_html_str(
            cls,
            recording_name: str = RECORDING_DEFAULT_NAME,
    ):
        cls._to_str(
            recording_name,
            'html',
        )

    @classmethod
    def to_json_file(
            cls,
            recording_name: str = RECORDING_DEFAULT_NAME,
            path: Path | str = DEFAULT_RECORDER_OUTPUT_PATH
    ):
        cls._to_file(
            recording_name,
            'json',
            path
        )

    @classmethod
    def to_json_str(
            cls,
            recording_name: str = RECORDING_DEFAULT_NAME,
    ):
        cls._to_str(
            recording_name,
            'json',
        )

    @classmethod
    def to_markdown_file(
            cls,
            recording_name: str = RECORDING_DEFAULT_NAME,
            path: Path | str = DEFAULT_RECORDER_OUTPUT_PATH
    ):
        cls._to_file(
            recording_name,
            'markdown',
            path
        )

    @classmethod
    def to_markdown_str(
            cls,
            recording_name: str = RECORDING_DEFAULT_NAME,
    ):
        cls._to_str(
            recording_name,
            'markdown',
        )
