# from __future__ import annotations
#
# from pathlib import Path
# from typing import TYPE_CHECKING, Literal
#
# from dandy.audio.connector import AudioConnector
# from dandy.audio.intelligence.intel import (
#     AudioSegmentsTranscriptionIntel,
#     AudioTranscriptionIntel,
#     AudioWordsTranscriptionIntel,
# )
# from dandy.core.service.service import BaseService
# from dandy.llm.prompt.typing import PromptOrStr, PromptOrStrOrNone
# from dandy.recorder.utils import generate_new_recorder_event_id
#
# if TYPE_CHECKING:
#     from dandy.audio.mixin import AudioServiceMixin
#
# AudioFormatLiteralType = Literal['flac', 'mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'ogg', 'wav', 'webm']
#
#
# class AudioService(BaseService['AudioServiceMixin']):
#     obj: AudioServiceMixin
#
#     def __post_init__(self):
#         self.event_id = generate_new_recorder_event_id()
#
#         self.obj.audio_config.http_request_intel.data = {
#             'model': self.obj.audio_config.model,
#         }
#
#     def transcribe(
#             self,
#             audio_format: AudioFormatLiteralType,
#             prompt: PromptOrStrOrNone = None,
#             audio_url: str | None = None,
#             audio_file_path: str | Path | None = None,
#             audio_bytes_data: bytes | None = None,
#     ) -> AudioTranscriptionIntel:
#         audio_connector = AudioConnector(
#             event_id=self.event_id,
#             http_request_intel=self.obj.audio_config.http_request_intel,
#             intel_class=AudioTranscriptionIntel,
#             audio_format=audio_format,
#             audio_url=audio_url,
#             audio_file_path=audio_file_path,
#             audio_bytes_data=audio_bytes_data,
#         )
#
#         return audio_connector.request_to_intel(
#             prompt=prompt,
#         )
#
#     def segments_transcribe(
#             self,
#             audio_format: AudioFormatLiteralType,
#             prompt: PromptOrStrOrNone = None,
#             audio_url: str | None = None,
#             audio_file_path: str | Path | None = None,
#             audio_bytes_data: bytes | None = None,
#     ) -> AudioSegmentsTranscriptionIntel:
#         audio_connector = AudioConnector(
#             event_id=self.event_id,
#             http_request_intel=self.obj.audio_config.http_request_intel,
#             intel_class=AudioTranscriptionIntel,
#             audio_format=audio_format,
#             audio_url=audio_url,
#             audio_file_path=audio_file_path,
#             audio_bytes_data=audio_bytes_data,
#         )
#
#         return audio_connector.request_to_intel(
#             prompt=prompt,
#             response_format='verbose_json',
#             verbose_format='word',
#         )
#
#     def words_transcribe(
#             self,
#             audio_format: AudioFormatLiteralType,
#             prompt: PromptOrStrOrNone = None,
#             audio_url: str | None = None,
#             audio_file_path: str | Path | None = None,
#             audio_bytes_data: bytes | None = None,
#     ) -> AudioWordsTranscriptionIntel:
#         audio_connector = AudioConnector(
#             event_id=self.event_id,
#             http_request_intel=self.obj.audio_config.http_request_intel,
#             intel_class=AudioWordsTranscriptionIntel,
#             audio_format=audio_format,
#             audio_url=audio_url,
#             audio_file_path=audio_file_path,
#             audio_bytes_data=audio_bytes_data,
#         )
#
#         return audio_connector.request_to_intel(
#             prompt=prompt,
#             response_format='verbose_json',
#             verbose_format='word',
#         )
#
#     def reset_service(self):
#         pass
#
