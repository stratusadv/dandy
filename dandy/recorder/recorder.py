import json
from pathlib import Path

from typing_extensions import Dict

from dandy.conf import settings
from dandy.constants import RECORDER_OUTPUT_DIRECTORY, RECORDING_DEFAULT_NAME
from dandy.core.singleton import Singleton
from dandy.recorder.events import Event
from dandy.recorder.exceptions import RecorderCriticalException
from dandy.recorder.recording import Recording
from dandy.recorder.renderer.html import HtmlRecordingRenderer
from dandy.recorder.renderer.markdown import MarkdownRecordingRenderer
from dandy.recorder.renderer.json import JsonRecordingRenderer

_DEFAULT_RECORDER_OUTPUT_PATH = Path(settings.BASE_PATH, RECORDER_OUTPUT_DIRECTORY)


class Recorder(Singleton):
    recordings: Dict[str, Recording] = dict()

    @classmethod
    def add_event(cls, event: Event):
        for recording in cls.recordings.values():
            if recording.is_running:
                recording.event_manager.add_event(event)

    @classmethod
    def check_recording_is_valid(cls, recording_name: str = RECORDING_DEFAULT_NAME) -> bool:
        if recording_name not in cls.recordings:
            choices_message = ''

            if len(cls.recordings.keys()) == 0:
                choices_message = f' Choices are {list(cls.recordings.keys())}'

            raise RecorderCriticalException(f'Debug recording "{recording_name}" does not exist. {choices_message}')

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
    def to_html_file(cls, recording_name: str = RECORDING_DEFAULT_NAME, path=_DEFAULT_RECORDER_OUTPUT_PATH):
        cls.check_recording_is_valid(recording_name)
        HtmlRecordingRenderer(recording=cls.recordings[recording_name]).to_file(path)

    @classmethod
    def to_html_str(cls, recording_name: str = RECORDING_DEFAULT_NAME) -> str:
        cls.check_recording_is_valid(recording_name)
        HtmlRecordingRenderer(recording=cls.recordings[recording_name]).to_str()

    @classmethod
    def to_json_file(cls, recording_name: str = RECORDING_DEFAULT_NAME, path=_DEFAULT_RECORDER_OUTPUT_PATH):
        cls.check_recording_is_valid(recording_name)
        JsonRecordingRenderer(recording=cls.recordings[recording_name]).to_file(path)

    @classmethod
    def to_json_str(cls, recording_name: str = RECORDING_DEFAULT_NAME) -> str:
        cls.check_recording_is_valid(recording_name)
        JsonRecordingRenderer(recording=cls.recordings[recording_name]).to_str()
