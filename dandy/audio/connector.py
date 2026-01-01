import io
from pathlib import Path
from typing import Literal

from dandy.audio.exceptions import AudioRecoverableException
from dandy.core.connector.connector import BaseConnector
from dandy.http.connector import HttpConnector
from dandy.http.intelligence.intel import HttpRequestIntel
from dandy.intel.factory import IntelFactory
from dandy.intel.typing import IntelType
from dandy.llm.prompt.typing import PromptOrStrOrNone


class AudioConnector(BaseConnector):
    def __init__(
            self,
            event_id: str,
            http_request_intel: HttpRequestIntel,
            intel_class: type[IntelType],
            audio_format: str,
            audio_url: str | None = None,
            audio_file_path: str | Path | None = None,
            audio_bytes_data: bytes | None = None,

    ):
        self._event_id = event_id
        self._http_request_intel = http_request_intel
        self._intel_class = intel_class
        self._http_connector = HttpConnector()

        if audio_url:
            raise NotImplementedError('Audio transcription from url is not implemented yet')

        if audio_file_path:
            with open(audio_file_path, 'rb') as f:
                audio_bytes_data = f.read()

        if audio_bytes_data is None:
            message = 'The AudioService requires audio_url, audio_file_path or audio_bytes_data.'
            raise ValueError(message)

        self._http_request_intel.files = {
            'file': ('recording.mp3', io.BytesIO(audio_bytes_data), f'audio/{audio_format}'),
        }

    def request_to_intel(
            self,
            prompt: PromptOrStrOrNone = None,
            response_format: Literal['json', 'diarized_json', 'verbose_json'] = 'json',
            verbose_format: Literal['word', 'segment'] = 'word',
    ) -> IntelType:
        if prompt is not None:
            self._http_request_intel.data['prompt'] = prompt

        self._http_request_intel.data['response_format'] = response_format

        if response_format == 'verbose_json':
            self._http_request_intel.data['timestamp_granularities'] = [verbose_format]

        response_intel = self._http_connector.request_to_response(
            self._http_request_intel
        )

        intel_object = IntelFactory.json_str_to_intel_object(
            json_str=response_intel.json_str, intel=self._intel_class
        )

        if intel_object is not None:

            return intel_object

        else:
            message = 'Failed to validate response into intel object.'
            raise AudioRecoverableException(message)
