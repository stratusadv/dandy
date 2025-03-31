import json
from pathlib import Path

from typing_extensions import Dict

from dandy.conf import settings
from dandy.constants import RECORDER_OUTPUT_DIRECTORY, RECORDING_DEFAULT_NAME
from dandy.core.singleton import Singleton
from dandy.recorder.events import BaseEvent
from dandy.recorder.exceptions import RecorderCriticalException
from dandy.recorder.recording import Recording

_DEFAULT_DEBUG_OUTPUT_PATH = Path(settings.BASE_PATH, RECORDER_OUTPUT_DIRECTORY)


class Recorder(Singleton):
    recordings: Dict[str, Recording] = dict()

    @classmethod
    def _recording_allowed(cls) -> bool:
        return settings.ALLOW_DEBUG_RECORDING

    @classmethod
    def add_event(cls, event: BaseEvent):
        if cls._recording_allowed():
            for debugger in cls.recordings.values():
                if debugger.is_recording:
                    debugger.add_event(event)

    @classmethod
    def clear(cls):
        if cls._recording_allowed():
            cls.recordings = dict()

    @classmethod
    def start_recording(cls, recording_name: str = RECORDING_DEFAULT_NAME):
        if cls._recording_allowed():
            cls.recordings[recording_name] = Recording(name=recording_name)
            cls.recordings[recording_name].start()

    @classmethod
    def stop_recording(cls, recording_name: str = RECORDING_DEFAULT_NAME):
        if cls._recording_allowed():
            if recording_name not in cls.recordings:
                choices_message = ''

                if len(cls.recordings.keys()) == 0:
                    choices_message = f' Choices are {list(cls.recordings.keys())}'

                raise RecorderCriticalException(f'Debug recording "{recording_name}" does not exist. {choices_message}')

            cls.recordings[recording_name].stop()

    @classmethod
    def stop_all_recording(cls):
        if cls._recording_allowed():
            for debugger in cls.recordings.values():
                debugger.stop()

    @classmethod
    @property
    def is_recording(cls):
        if cls._recording_allowed():
            return any([debugger.is_recording for debugger in cls.recordings.values()])

    @classmethod
    def to_html_file(cls, recording_name: str = RECORDING_DEFAULT_NAME, path=_DEFAULT_DEBUG_OUTPUT_PATH):
        if cls._recording_allowed():
            cls.recordings[recording_name].to_html_file(path)

    @classmethod
    def to_html_str(cls, recording_name: str = RECORDING_DEFAULT_NAME) -> str:
        if cls._recording_allowed():
            return cls.recordings[recording_name].to_html_str()
        else:
            return 'DEBUG RECORDING DISABLED'

    @classmethod
    def to_json_file(cls, recording_name: str = RECORDING_DEFAULT_NAME, path=_DEFAULT_DEBUG_OUTPUT_PATH):
        if cls._recording_allowed():
            cls.recordings[recording_name].to_json_file(path)

    @classmethod
    def to_json_str(cls, recording_name: str = RECORDING_DEFAULT_NAME) -> str:
        if cls._recording_allowed():
            return cls.recordings[recording_name].to_json_str()
        else:
            return json.dumps({'output': 'DEBUG RECORDING DISABLED'}, indent=4)
